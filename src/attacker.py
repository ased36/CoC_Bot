from utils import *
try:
    import configs
    from configs import *
except:
    import configs_build as configs
    from configs_build import *

class Attacker:
    def __init__(self):
        self.assets = Asset_Manager.attacker_assets
        self.misc_assets = Asset_Manager.misc_assets

    # ============================================================
    # 📱 Screen Interaction
    # ============================================================
    
    def _click_okay(self, timeout=5):
        return click_with_timeout(
            lambda: Frame_Handler.locate(self.assets["okay"], thresh=0.9),
            timeout=timeout,
        )
    
    def _click_surrender(self, timeout=5):
        return click_with_timeout(
            lambda: Frame_Handler.locate(self.assets["surrender"], thresh=0.9),
            timeout=timeout
        )
    
    def _click_end_battle(self, timeout=5):
        return click_with_timeout(
            lambda: Frame_Handler.locate(self.assets["end_battle"], thresh=0.9),
            timeout=timeout
        )
    
    def _click_return_home(self, timeout=5):
        return click_with_timeout(
            lambda: Frame_Handler.locate(self.assets["return_home"], thresh=0.9),
            timeout=timeout
        )

    def _wait_battle_end(self, location, timeout):
        import time

        # Let the battle play out and leave through the results screen instead of restarting CoC
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self._click_return_home(timeout=2):
                time.sleep(3)
                self._click_okay(timeout=2)
                TEMP_CACHE["location"] = location
                logger.info(f"Battle ended after {int(time.time() - start_time)}s, returned home")
                return True
            time.sleep(2)
        logger.warning(f"Return Home not found within {timeout}s, restarting CoC instead")
        return False

    # ============================================================
    # 🗺️ Deploy zone (zoomed out enemy village)
    # ============================================================

    # Screen parts that are not the village (x1, y1, x2, y2): loot box, timer, resources, buttons, boosts, troop bar
    HUD_BOXES = [
        (0.00, 0.00, 0.17, 0.29), (0.42, 0.00, 0.57, 0.10), (0.77, 0.00, 1.00, 0.23),
        (0.00, 0.69, 0.14, 0.80), (0.13, 0.69, 0.47, 0.80), (0.82, 0.63, 1.00, 0.80), (0.00, 0.80, 1.00, 1.00),
    ]
    CORNER_ANGLES = {"right": 0, "bottom": 90, "left": 180, "top": 270} # screen angles, y pointing down

    @classmethod
    def _in_hud(cls, x, y):
        return any(x1 <= x <= x2 and y1 <= y <= y2 for x1, y1, x2, y2 in cls.HUD_BOXES)

    def _deploy_ring(self, frame):
        """Outline of the red no-deploy line, as {angle: (center, radius)} in pixels, seen from the village center.
        Troops can only be dropped outside every red line, so the farthest red pixel in each direction is the edge."""
        import numpy as np
        h, w = frame.shape[:2]
        f = frame.astype(int)
        red = (f[..., 0] > 170) & (f[..., 0] - f[..., 1] > 90) & (f[..., 2] < 90)
        for x1, y1, x2, y2 in self.HUD_BOXES: red[int(y1 * h):int(y2 * h), int(x1 * w):int(x2 * w)] = False
        import cv2
        ys, xs = np.nonzero(red)
        if len(xs) < 500: return None
        cx, cy = np.median(xs), np.median(ys)
        # Parts of the line hide behind buildings and the HUD; outside the convex hull of everything red is always free
        hull = cv2.convexHull(np.stack([xs, ys], axis=1).astype(np.int32))
        radius = np.zeros(180)
        for i in range(180): # 2 degree steps: walk out from the center until leaving the hull
            t = np.radians(i * 2)
            lo, hi = 0.0, float(w)
            while hi - lo > 1:
                mid = (lo + hi) / 2
                inside = cv2.pointPolygonTest(hull, (float(cx + mid * np.cos(t)), float(cy + mid * np.sin(t))), False) >= 0
                lo, hi = (mid, hi) if inside else (lo, mid)
            radius[i] = lo
        return (cx, cy), radius

    def _deploy_points(self, ring, corner, n, spread=35, margin=0.035):
        """n screen points just outside the red line around a corner (name, or an angle in degrees), spread over both of its edges."""
        import numpy as np
        (cx, cy), radius = ring
        h, w = 1080, 1920 # ring is measured on 1920x1080 frames
        points = []
        # The bottom corner sits under the troop bar: widen the spread onto its two visible edges until n points fit
        for width in (spread, spread + 20, spread + 35):
            for _ in range(n * 10):
                a = (corner if isinstance(corner, (int, float)) else self.CORNER_ANGLES[corner]) + np.random.uniform(-width, width)
                edge = radius[int(round(a / 2)) % 180]
                ex, ey = (cx + edge * np.cos(np.radians(a))) / w, (cy + edge * np.sin(np.radians(a))) / h
                # Where the hull ends at a HUD box or the screen edge the real line is hidden further out: no safe point there
                if self._in_hud(ex, ey) or any(self._in_hud(ex + dx, ey + dy) for dx, dy in ((0.015, 0), (-0.015, 0), (0, 0.045), (0, -0.03))): continue
                if ey < 0.045 or not 0.02 <= ex <= 0.98: continue # cut by the screen edge (after the view moved)
                r = edge + margin * w + np.random.uniform(0, 0.015) * w
                x, y = (cx + r * np.cos(np.radians(a))) / w, (cy + r * np.sin(np.radians(a))) / h
                if 0.02 <= x <= 0.98 and 0.03 <= y and not self._in_hud(x, y): points.append((x, y))
                if len(points) == n: return points
        return points

    def _inside_points(self, ring, n):
        """n random screen points inside the village (for spells)."""
        import numpy as np
        (cx, cy), radius = ring
        points = []
        while len(points) < n:
            a = np.random.uniform(0, 360)
            r = radius[int(round(a / 2)) % 180] * np.random.uniform(0.15, 0.75)
            x, y = (cx + r * np.cos(np.radians(a))) / 1920, (cy + r * np.sin(np.radians(a))) / 1080
            if not self._in_hud(x, y): points.append((x, y))
        return points

    # ============================================================
    # 🃏 Scripted attack (attacks/<style>.yaml, docs/SALDIRI-STILI.md)
    # ============================================================

    # The troop bar cards change size: with empty slots shown (19:15, 8 cards + 3 slots) they are ~0.8 of the
    # pictures in assets/attacker/cards. Card middle and health bar move with the size (measured at 1.0 and 0.8)
    CARD_SCALES = (0.75, 0.8, 0.85, 0.9, 0.95, 1.0, 1.05)
    card_scale = 1.0

    @property
    def CARD_Y(self): # middle of the troop bar cards at 1920x1080
        return 0.905 + (1 - self.card_scale) * 0.075

    def _card_templates(self):
        import os, cv2
        if not hasattr(self, "_cards"):
            path = Asset_Manager.resource_path("assets/attacker/cards")
            self._cards = {f[:-4]: cv2.cvtColor(cv2.imread(str(path / f)), cv2.COLOR_BGR2RGB) for f in os.listdir(path) if f.endswith(".png")}
        return self._cards

    def _find_cards(self, frame):
        """{card name: x of its center} for the cards in the troop bar; clan castle cards come after ours, so the leftmost match wins.
        The card size is the one where the three best matching cards match best (a selected card is raised and a
        used up one is gray, so no single card decides), then every card is looked for at that size."""
        import cv2, numpy as np
        bar = frame[int(frame.shape[0] * 0.80):]
        tpls = self._card_templates()
        def scaled(tpl, s): return cv2.resize(tpl, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        def fit(s): return sum(sorted(cv2.matchTemplate(bar, scaled(t, s), cv2.TM_CCOEFF_NORMED).max() for t in tpls.values())[-3:])
        self.card_scale = max(self.CARD_SCALES, key=fit)
        found = {}
        for name, tpl in tpls.items():
            t = scaled(tpl, self.card_scale)
            res = cv2.matchTemplate(bar, t, cv2.TM_CCOEFF_NORMED)
            xs = np.nonzero(res.max(axis=0) >= 0.85)[0]
            if len(xs): found[name] = (xs.min() + t.shape[1] / 2) / frame.shape[1]
        # The siege card changes its picture (machine, "!"), but it always sits between the troops and the first hero
        troop, hero = found.get("super_barbarian"), found.get("king")
        if not any(n.startswith("siege") for n in found) and troop and hero and hero - troop > 0.1:
            found["siege"] = (troop + hero) / 2
        return found

    def _card_empty(self, x):
        # A used up card turns gray
        y = self.CARD_Y
        section = Frame_Handler.get_frame_section(x - 0.01, y - 0.01, x + 0.01, y + 0.01, grayscale=False).astype(int)
        return (abs(section[..., 0] - section[..., 1]).max() < 8) and (abs(section[..., 1] - section[..., 2]).max() < 8)

    def _card_deployed(self, x, frame=None):
        # A siege machine or hero on the field shows a health bar above its card (~850 green pixels at full health and
        # size 1.0, 0 before). The bar is at 0.795-0.815 for size 1.0 and 0.837-0.845 for 0.8
        if frame is None: frame = Frame_Handler.get_frame(grayscale=False)
        y = 0.805 + (1 - self.card_scale) * 0.18
        s = Frame_Handler.crop(frame, x - 0.02, y - 0.01, x + 0.02, y + 0.01).astype(int)
        return int(((s[..., 1] > 150) & (s[..., 1] - s[..., 0] > 50) & (s[..., 1] - s[..., 2] > 50)).sum()) > 400 * self.card_scale

    def _wait_deployed(self, x, timeout=2.0):
        # The bar shows up a moment after the drop (the hero or machine walks in)
        import time
        start = time.time()
        while time.time() - start < timeout:
            if self._card_deployed(x): return True
            time.sleep(0.2)
        return False

    def _click_button(self, name, timeout=3, scales=(0.6, 0.7, 0.8, 0.9, 1.0, 1.1)):
        """Tap a button image found at any of a few sizes (the button pictures were taken at other UI sizes)."""
        import time, cv2
        templates = [cv2.resize(self.assets[name], None, fx=s, fy=s, interpolation=cv2.INTER_AREA) for s in scales]
        start = time.time()
        while time.time() - start < timeout:
            for x, y in Frame_Handler.batch_locate(templates, grayscale=False, thresh=0.85):
                if x is not None:
                    self._tap(x, y, spread=0.003)
                    return True
            time.sleep(0.3)
        return False

    def _show_bottom(self):
        """Drag the view up so the bottom corner comes out from under the troop bar; returns the deploy line seen then.
        Nothing is selected while dragging, so the drag only moves the view."""
        import time
        self._deselect()
        time.sleep(0.2)
        Input_Handler.swipe(0.5, 0.62, 0.5, 0.36, duration=400, hold_end_time=300, inter_points=8)
        time.sleep(0.8)
        return self._deploy_ring(Frame_Handler.get_frame(grayscale=False))

    @staticmethod
    def _deselect():
        # Tap the empty left end of the troop bar: a stray tap on the field later then drops nothing
        Input_Handler.click(0.01, 0.905)

    @staticmethod
    def _pause(span):
        import time, random
        time.sleep(random.uniform(*span))

    @staticmethod
    def load_style(name):
        import yaml
        with open(Asset_Manager.resource_path(f"attacks/{name}.yaml"), encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _leftover_troops(self, ring, troop_x, select_card, margins=(0.06, 0.09, 0.12), pause=0.25, around=None, spread=60):
        """Troops a tap or a drag could not drop (red area): select the card again and drop them one by one further out.
        Whole visible edges, not only corners, further out each round, until the card is empty (at most 60 taps).
        The bottom corner can stay hidden even after the view moved (18:47: 0 points, 30 troops left).
        The card is looked at before every tap: once it is empty the game selects the siege card and a further tap
        would drop the machine here. pause: the wait between taps on top of that look (Emre 20:55 "too slow")."""
        import time, random
        time.sleep(0.4)
        if self._card_empty(troop_x): return
        visible = around or [c for c in self.CORNER_ANGLES if c != "bottom"]
        select_card()
        n = 0
        for margin in margins:
            extra = [p for c in visible for p in self._deploy_points(ring, c, 10, spread=spread, margin=margin)]
            random.shuffle(extra)
            for x, y in extra:
                time.sleep(pause)
                if self._card_empty(troop_x) or n >= 60: break
                self._tap(x, y)
                n += 1
            if self._card_empty(troop_x) or n >= 60: break
        logger.info(f"Leftover troops: {n} more taps, card {'empty' if self._card_empty(troop_x) else 'still not empty'}")

    # Where a held finger may go: inside the screen, above the troop bar
    SAFE_BOX = (0.03, 0.06, 0.97, 0.78)

    def _ring_point(self, ring, angle, margin):
        """Screen point at angle (0 right, 90 bottom, 180 left, 270 top) margin (part of the screen width) outside the red line."""
        import numpy as np
        (cx, cy), radius = ring
        r = radius[int(round(angle / 2)) % 180] + margin * 1920
        x, y = (cx + r * np.cos(np.radians(angle))) / 1920, (cy + r * np.sin(np.radians(angle))) / 1080
        x1, y1, x2, y2 = self.SAFE_BOX
        return min(max(x, x1), x2), min(max(y, y1), y2)

    def _outward(self, ring, point, push):
        """point moved push (part of the screen width) further away from the village center."""
        import numpy as np
        (cx, cy), _ = ring
        x, y = point[0] * 1920, point[1] * 1080
        d = max(np.hypot(x - cx, y - cy), 1)
        x, y = (x + (x - cx) / d * push * 1920) / 1920, (y + (y - cy) / d * push * 1920) / 1080
        x1, y1, x2, y2 = self.SAFE_BOX
        return min(max(x, x1), x2), min(max(y, y1), y2)

    # Emre's drop sweeps (27 sweeps, recordings 01.11 19:12 and 20:33) seen from the screen point (0.48, 0.47), in
    # 15 degree steps from 0 (right, 90 bottom): the middle of where his finger went and its outer quarter, as
    # distance / screen height. After the search the view is always as far out and centered, so the map's outer grass
    # band is on the same screen spot for every village: the outer quarter stays on it, the middle is near big villages
    EMRE_CENTER = (0.48, 0.47)
    EMRE_MID = (0.547, 0.444, 0.358, 0.313, 0.291, 0.294, 0.303, 0.313, 0.344, 0.405, 0.442, 0.518,
                0.587, 0.454, 0.392, 0.384, 0.387, 0.396, 0.387, 0.385, 0.394, 0.427, 0.513, 0.606)
    EMRE_OUTER = (0.641, 0.526, 0.442, 0.356, 0.318, 0.312, 0.314, 0.32, 0.389, 0.428, 0.497, 0.592,
                  0.688, 0.585, 0.427, 0.428, 0.43, 0.437, 0.47, 0.477, 0.475, 0.474, 0.586, 0.665)

    def _emre_ring(self, profile, shift=(0, 0)):
        """A ring in the form _deploy_ring returns ((center px), radius px per 2 degrees) from one of Emre's profiles,
        moved with the view (shift in px)."""
        import numpy as np
        bins = np.arange(len(profile)) * 15 + 7.5
        angles = np.arange(180) * 2
        radius = np.interp(angles, np.r_[bins - 360, bins, bins + 360], np.r_[profile, profile, profile]) * 1080
        return (self.EMRE_CENTER[0] * 1920 + shift[0], self.EMRE_CENTER[1] * 1080 + shift[1]), radius

    def _sweep_path(self, ring, start, sweep, lead_in=0.0, margins=(-0.01, 0.01)):
        """Points of one finger sweep from angle start over sweep degrees along the ring (Emre's outer band), drifting
        slowly in and out like a hand. The recorded sweeps even cut through the village in places: troops only land
        outside the line, so a drift inside only costs a moment. The finger never starts on a HUD button. The outer band
        is the map's edge: a press that starts past it (forest, water) is ignored and the whole sweep drops nothing
        (21:10, card stayed x60). Emre likes the sweep just past the band (21:17), so it starts inside it (lead_in < 0)
        and widens over the first part."""
        import numpy as np, random
        for _ in range(12):
            if not self._in_hud(*self._ring_point(ring, start, lead_in)): break
            start += 8 if sweep > 0 else -8
        phase, waves, base = random.uniform(0, 2 * np.pi), random.uniform(1.5, 3), random.uniform(*margins)
        n = max(int(abs(sweep) / 5), 8)
        def margin(i): return base + 0.012 * np.sin(phase + waves * 2 * np.pi * i / n) + lead_in * max(0.0, 1 - i / (0.15 * n))
        return [self._ring_point(ring, start + sweep * i / n, margin(i)) for i in range(n + 1)]

    def _watch_empty(self, x, shots=None):
        """Watch a card from a second thread while a finger is held (a frame takes too long to look between finger steps).
        Returns (empty, done) events: empty is set once the card is gray, set done to stop watching.
        With shots, the frames it looks at are kept too (what the field did during the hold)."""
        import threading, time, cv2
        empty, done = threading.Event(), threading.Event()
        t0 = time.time()
        def run():
            n = 0
            while not done.is_set() and not empty.is_set():
                try:
                    if self._card_empty(x): empty.set()
                    if shots is not None and n < 40:
                        cv2.imwrite(str(shots / f"hold_{int((time.time() - t0) * 1000):05d}.png"), cv2.cvtColor(Frame_Handler.cached_frame, cv2.COLOR_RGB2BGR))
                        n += 1
                except Exception:
                    return
                time.sleep(0.05)
        threading.Thread(target=run, daemon=True).start()
        return empty, done

    @classmethod
    def _red_area_from(cls, before, after):
        """The red area the game shows right after a troop is refused (measured 22:32, 22:41): the whole no-deploy zone
        gets a tint (Lab a* down ~5-15 over the village, sharp stepped edges) that fades out within ~1.5 s.
        before: a frame without the tint, after: a frame right after the refused tap. Returns the ring of that zone
        ((center px), radius px per 2 degrees, as _deploy_ring) or None when it is not seen."""
        import cv2, numpy as np
        a = cv2.cvtColor(before, cv2.COLOR_RGB2LAB).astype(np.float32)[..., 1]
        b = cv2.cvtColor(after, cv2.COLOR_RGB2LAB).astype(np.float32)[..., 1]
        d = cv2.GaussianBlur(cv2.medianBlur(b - a, 5), (0, 0), 2)
        h, w = d.shape
        # The tint lowers a* (22:32, 22:58: whole zone clearly); either sign is accepted, the larger zone wins
        m = ((d < -2.5) if (d < -2.5).sum() >= (d > 2.5).sum() else (d > 2.5)).astype(np.uint8)
        hud = np.zeros_like(m)
        for x1, y1, x2, y2 in cls.HUD_BOXES: hud[int(y1 * h):int(y2 * h), int(x1 * w):int(x2 * w)] = 1
        m[hud > 0] = 0
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)) # walking troops and their shadows
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
        n, lab, st, cent = cv2.connectedComponentsWithStats(m)
        if n < 2: return None
        big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
        if st[big, cv2.CC_STAT_AREA] < 0.08 * h * w: return None # a few moving troops, not the zone (or not shown yet)
        cs, _ = cv2.findContours((lab == big).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        pts = max(cs, key=cv2.contourArea)[:, 0, :].astype(float)
        # Edge points that touch a HUD box or the screen edge are where the zone is hidden, not where it ends
        near = cv2.dilate(hud, np.ones((21, 21), np.uint8))
        xi, yi = pts[:, 0].astype(int), pts[:, 1].astype(int)
        hidden = (near[yi, xi] > 0) | (xi < 10) | (xi > w - 11) | (yi < 10)
        cx, cy = cent[big]
        ang = (np.degrees(np.arctan2(pts[:, 1] - cy, pts[:, 0] - cx)) + 360) % 360
        r = np.hypot(pts[:, 0] - cx, pts[:, 1] - cy)
        radius = np.full(180, np.nan)
        for i in range(180):
            sel = ((ang >= i * 2 - 1) & (ang < i * 2 + 1) | (ang >= i * 2 + 359)) & ~hidden
            if sel.any(): radius[i] = r[sel].max()
        ok = ~np.isnan(radius)
        if ok.sum() < 60: return None
        idx = np.arange(180)
        radius = np.interp(idx, np.r_[idx[ok] - 180, idx[ok], idx[ok] + 180], np.r_[radius[ok], radius[ok], radius[ok]])
        # Narrow spikes (troops walking at the edge) and notches (a corner under the HUD) are not the zone's shape:
        # circular median over 22 degrees
        wrap = np.r_[radius[-5:], radius, radius[:5]]
        radius = np.array([np.median(wrap[i:i + 11]) for i in range(180)])
        return (cx * 1920 / w, cy * 1080 / h), radius * 1920 / w

    def _start_battle(self, ring_mid, ring_out):
        """The troop card is selected: one troop on a spot that is surely on the map and outside the red line starts the
        battle (only then does a refused tap show the red area; before it a tap selects a building). Spots from wide to
        narrow parts of the map; the battle is on once the scouting Next button is gone (22:47: the first spot was off a
        stone themed map). Returns whether it started."""
        import time, random
        # First the screen's left and right edges, where Emre's sweeps start (farthest from any village; 22:51 every
        # spot near the band was inside a big village's red area), then spots along his paths
        edges = random.sample([(random.uniform(0.04, 0.07), random.uniform(0.42, 0.55)), (random.uniform(0.93, 0.96), random.uniform(0.38, 0.52))], 2)
        sides = random.sample((0, 180), 2)
        spots = edges + [self._ring_point(ring_out, a + random.uniform(-6, 6), m) for m in (-0.05, 0.03) for a in sides]
        spots += [self._ring_point(ring_out, a, -0.03) for a in (30, 150, 210, 330)]
        for x, y in spots:
            if self._in_hud(x, y): continue
            self._tap(x, y, spread=0.004)
            time.sleep(random.uniform(0.3, 0.45))
            if self._wait_village(timeout=0.3) is None: return True
        return False

    def _reveal_red_area(self, before, shots=None):
        """The troop card is selected and the battle is on: one tap on the middle of the village (red area, nothing
        drops) and frames as fast as they come, while the tint is on. before: a frame without the tint (taken before the
        troop that started the battle). Returns the zone's ring or None."""
        import time, cv2
        guess = self._deploy_ring(before)
        cx, cy = (guess[0][0] / 1920, guess[0][1] / 1080) if guess else self.EMRE_CENTER
        self._tap(cx, cy, spread=0.004)
        t0, ring, after = time.time(), None, before
        while ring is None and time.time() - t0 < 1.2:
            after = Frame_Handler.get_frame(grayscale=False)
            ring = self._red_area_from(before, after)
        if shots is not None:
            cv2.imwrite(str(shots / "red_before.png"), cv2.cvtColor(before, cv2.COLOR_RGB2BGR))
            cv2.imwrite(str(shots / "red_after.png"), cv2.cvtColor(after, cv2.COLOR_RGB2BGR))
        logger.info("Red area " + ("read" if ring else "not seen, using the recorded paths"))
        return ring

    @staticmethod
    def _view_shift(a, b):
        """How far the view moved between two frames (dx, dy in pixels), from the field above the troop bar."""
        import cv2, numpy as np
        def prep(f): return cv2.resize(cv2.cvtColor(f[:int(f.shape[0] * 0.78)], cv2.COLOR_RGB2GRAY), None, fx=0.25, fy=0.25).astype(np.float32)
        (dx, dy), _ = cv2.phaseCorrelate(prep(a), prep(b))
        return dx * 4, dy * 4

    def _deploy_spread(self, style, ring, cards, shots):
        """Emre's attack (recorded 01.11 19:12-19:27, docs/SALDIRI-STILI.md Stil 2, attacks/yayma.yaml): the Royal Champion
        alone on one side with her ability at once, the troops spread by holding the finger and sweeping around the
        village, then the siege machine and the other heroes on one spot, the bat spells on the same spot.
        Returns (first drop time, abilities)."""
        import time, random
        troops, heroes, spells, siege = (style.get(k) or {} for k in ("troops", "heroes", "spells", "siege"))
        def tap_card(name):
            self._tap(cards[name], self.CARD_Y, spread=0.006)
            self._pause(style.get("card_to_drop", [0.3, 0.7]))

        # Not the line guessed from red building parts (too tight, 20:30: 7 of 60 dropped) but Emre's own paths:
        # spots and leftovers on the middle of his sweeps, the sweeps on their outer quarter. If the view moves
        # during the attack the rings move with it (the shift is measured from a fresh frame)
        moved = [0.0, 0.0]
        ring, ring_out = self._emre_ring(self.EMRE_MID), self._emre_ring(self.EMRE_OUTER)
        # Once the game has shown the real red area (Emre 1A, 22:32) everything goes by that line instead
        red = None
        last = {"frame": Frame_Handler.get_frame(grayscale=False)}
        def fresh_ring(label):
            nonlocal ring, ring_out, red
            frame = Frame_Handler.get_frame(grayscale=False)
            dx, dy = self._view_shift(last["frame"], frame)
            last["frame"] = frame
            if abs(dx) > 15 or abs(dy) > 15:
                logger.warning(f"View moved {dx:+.0f}, {dy:+.0f} px ({label})")
                moved[0] += dx
                moved[1] += dy
                ring, ring_out = self._emre_ring(self.EMRE_MID, moved), self._emre_ring(self.EMRE_OUTER, moved)
                if red: red = ((red[0][0] + dx, red[0][1] + dy), red[1])

        # Two spots: the heroes' spot and the champion's spot on another side (a side whose edge is visible)
        spots = []
        for side in random.sample(list(self.CORNER_ANGLES), 4):
            p = self._deploy_points(ring_out, side, 1, spread=20, margin=0.01)
            if p: spots.append((side, p[0]))
        if not spots:
            logger.error("Attack: no visible edge to deploy on")
            return time.time(), []
        hero_side, hero_spot = spots[0]
        lead_side, lead_spot = spots[1] if len(spots) > 1 else spots[0]
        logger.info(f"Heroes {hero_side}, champion {lead_side}")
        def spot_again(side, old):
            # After the view moved a side can be hidden (the bottom under the troop bar after the pan back, 20:52: siege
            # and three heroes tapped on the old spot, now inside the village): then the next visible side
            if red:
                # Middle of a side, the side nearest the old one first (corners can be off the map, 23:03)
                first = {"right": 315, "left": 225, "top": random.choice((225, 315)), "bottom": 45}.get(side, 315)
                for a in [first] + [a for a in (315, 225, 45, 135) if a != first]:
                    p = self._deploy_points(red, a, 1, spread=15, margin=0.03)
                    if p: return side, p[0]
                return side, old
            for s in [side] + [s for s in ("left", "right", "top", "bottom") if s != side]:
                p = self._deploy_points(ring_out, s, 1, spread=20, margin=0.01)
                if p:
                    if s != side: logger.info(f"{side} is out of sight now, using {s}")
                    return s, p[0]
            return side, old

        abilities = []
        def ability(name):
            # Right after the drop (champion always, queen often) or later on its own random delay
            if random.random() < heroes.get("ability_now", {}).get(name, 0):
                self._pause([0.3, 0.8])
                self._tap(cards[name], self.CARD_Y, spread=0.006)
                logger.info(f"{name}: ability used right after the drop")
            else:
                abilities.append((time.time() + random.uniform(*heroes.get("ability_after", {}).get(name, [8, 12])), name))

        def place(name, spot, label):
            """The card is selected: drop it on the spot, a little off every time, further out when the red line refuses it."""
            for push in (0, -0.025, 0.03): # in first: past the outer band is off the map (21:10)
                self._tap(*self._outward(ring, spot, push), spread=0.008)
                if self._wait_deployed(cards[name], timeout=2.5): return True
                if self._card_empty(cards[name]): return True # used up (a siege machine already gone)
                logger.info(f"{label} did not land, trying further out")
            logger.warning(f"{label} could not be deployed")
            return False

        # Quick drops (Emre 20:55, "too slow"): card, spot, next card, without waiting for the health bar; whatever did
        # not land is dropped again further out once everything else is down
        dropped = []
        def quick(name, spot):
            tap_card(name)
            self._tap(*spot, spread=0.008)
            dropped.append((name, spot))
            if not name.startswith("siege"): ability(name)
            self._pause(heroes.get("gap", [0.25, 0.5]))

        lead = heroes.get("lead")
        battle_start = None
        def drop_lead():
            nonlocal battle_start
            if lead in cards and not self._card_deployed(cards[lead]):
                battle_start = battle_start or time.time()
                quick(lead, lead_spot)
        lead_first = random.random() < heroes.get("lead_first", 0.6)
        if lead_first: drop_lead()

        # Troops: hold and sweep (~7 troops a second while held). Two halves (top then bottom, or the other way, from the
        # left or the right) or one whole round. The hold ends a little before the card would run out; a second thread
        # lifts the finger earlier if the army is smaller (the next card would be selected); the rest go one by one
        troop_x = cards[troops["card"]]
        tap_card(troops["card"])
        if troops.get("red_line", True):
            # One troop where the map is widest starts the battle (before it a tap only selects a building), then a tap
            # on the middle of the village makes the game show the red area
            clean = Frame_Handler.get_frame(grayscale=False) # no tint yet
            started = battle_start is not None or self._start_battle(ring, ring_out)
            if started:
                battle_start = battle_start or time.time()
                red = self._reveal_red_area(clean, shots)
            else:
                logger.info("Battle did not start with one troop, using the recorded paths")
        hold = troops.get("count", 60) / troops.get("per_second", 7.3) * random.uniform(*troops.get("hold_share", [0.9, 0.96]))
        jitter = lambda: random.uniform(-12, 12)
        # pan (Emre's W / S keys, 20:38): the view is pushed up to show the bottom, the bottom half is swept, the view
        # comes back down and the top half is swept. Without it the bottom stays partly under the troop bar
        use_pan = random.random() < float(troops.get("pan", 0)) # a share of the attacks (Emre 1C), true = every attack
        pans = [None, None]
        per_side = troops.get("per_side")
        if per_side:
            # Emre 22:53: each of the village's four sides gets 13-15 troops in its own short sweep, the top two first,
            # then the view is pushed up (W) and the bottom two (the bottom stayed under the troop bar and got nothing)
            rate = troops.get("per_second", 7.3)
            counts = [random.randint(*per_side) for _ in range(3)]
            counts.append(max(troops.get("count", 60) - sum(counts), 8))
            centers = random.sample([225, 315], 2) + random.sample([45, 135], 2)
            sweeps = []
            for c in centers:
                # The middle of each side, where the band is widest: a big village reaches the map's corners and a
                # corner to corner sweep dropped little there (23:02: 60 -> 45 in four sweeps)
                d, width = random.choice((1, -1)), random.uniform(45, 60)
                sweeps.append((c - d * width / 2 + random.uniform(-4, 4), d * width))
            times = [k / rate for k in counts]
            pans = [None, None, -troops.get("pan_by", 0.3), None]
        elif use_pan or random.random() < troops.get("halves", 0.7):
            s1 = random.choice((0, 180))
            top_first = False if use_pan else random.random() < 0.5
            # top half from the left: 180 -> 360 over 270; from the right: 0 -> -180. Bottom half the other way round
            def half(s, top): return s + jitter(), (180 if (s == 180) == top else -180) + jitter()
            first = half(s1, top_first)
            sweeps = [first, half(180 - s1, not top_first)]
            share = random.uniform(0.45, 0.55)
            times = [hold * share, hold * (1 - share)]
            if use_pan:
                by = troops.get("pan_by", 0.3)
                pans = [-by, by]
        else:
            sweeps = [(random.choice((0, 180, 270)) + jitter(), random.choice((360, -360)))]
            times = [hold]
        def pan(dy):
            # Like BlueStacks' W / S: a quick swipe from the middle; a finger that moves at once moves the view, even with a
            # card selected. The rings follow from the shift measured afterwards
            Input_Handler.swipe(0.52, 0.51, 0.52 + random.uniform(-0.01, 0.01), 0.51 + dy, duration=300, hold_end_time=200, inter_points=6)
            time.sleep(random.uniform(0.4, 0.6))
        empty, done = self._watch_empty(troop_x, shots)
        battle_start = battle_start or time.time()
        try:
            for i, ((start, sweep), seconds) in enumerate(zip(sweeps, times)):
                if empty.is_set(): break
                if pans[i]: pan(pans[i])
                fresh_ring(f"before sweep {i + 1}")
                path = self._sweep_path(red, start, sweep, lead_in=0.0, margins=(0.015, 0.035)) if red else self._sweep_path(ring_out, start, sweep, lead_in=-0.03, margins=(0.0, 0.03))
                Input_Handler.drag_path(path, seconds, stop=empty.is_set,
                                        hold_start=random.uniform(*troops.get("hold_still", [0.35, 0.55])))
                self._pause(troops.get("sweep_pause", [0.25, 0.6]))
        finally:
            done.set()
        logger.info(f"Troops: {len(sweeps)} sweep(s), {hold:.1f}s held{', card ran out' if empty.is_set() else ''}")
        fresh_ring("after the sweeps")
        (hero_side, hero_spot), (lead_side, lead_spot) = spot_again(hero_side, hero_spot), spot_again(lead_side, lead_spot)
        if not empty.is_set():
            if red:
                self._leftover_troops(red, troop_x, lambda: tap_card(troops["card"]), margins=(0.03, 0.05, 0.07), pause=0.05, around=[225, 315, 45, 135], spread=25)
            else:
                self._leftover_troops(ring, troop_x, lambda: tap_card(troops["card"]), margins=(0.035, 0.055, 0.015), pause=0.05)

        if not lead_first: drop_lead()

        # Siege machine (usually first) and the other heroes on the heroes' spot. The siege card is tapped once only:
        # a second tap unloads it early
        group = [h for h in heroes.get("group", []) if h in cards]
        random.shuffle(group)
        siege_card = next((c for c in sorted(cards) if siege and c.startswith(siege.get("card", "-"))), None)
        if siege_card:
            group.insert(0 if random.random() < siege.get("first", 0.8) else random.randint(1, len(group)), siege_card)
        fresh_ring("before the heroes")
        hero_side, hero_spot = spot_again(hero_side, hero_spot)
        for name in group:
            quick(name, hero_spot)

        # Bat spells: quick taps on the heroes' spot (sometimes another side), drifting a little along the edge.
        # Only the last few taps look at the card: once it runs out the game selects the clan castle spell
        if spells.get("card") in cards:
            side, spot = (hero_side, hero_spot) if random.random() < spells.get("on_heroes", 0.85) or len(spots) < 2 else random.choice(spots[1:])
            count, x_spell = spells.get("count", 11), cards[spells["card"]]
            dx, dy = random.uniform(-0.03, 0.03), random.uniform(-0.03, 0.03)
            tap_card(spells["card"])
            for i in range(count + 3):
                if i >= count - 2 and self._card_empty(x_spell): break
                t = i / max(count - 1, 1)
                self._tap(spot[0] + dx * t, spot[1] + dy * t, spread=0.005)
                self._pause(spells.get("gap", [0.12, 0.17]))
            logger.info(f"Spells: {spells['card']} on {side}")

        # One look at the end: whatever did not land goes again, further out (its card is selected again first; a
        # landed siege machine is never touched again, a second tap unloads it)
        frame = Frame_Handler.get_frame(grayscale=False)
        for name, spot in dropped:
            if self._card_deployed(cards[name], frame) or (name.startswith("siege") and self._card_empty(cards[name])): continue
            logger.info(f"{name} did not land on the quick drop, again")
            tap_card(name)
            if place(name, spot, name) and not name.startswith("siege") and name not in [n for _, n in abilities]:
                ability(name)
        self._deselect()
        return battle_start, abilities

    def _deploy_corners(self, style, ring, cards, tap_card):
        """Corner style (attacks/super-barbar.yaml): per_corner taps on each corner, then siege and heroes. Returns (first drop time, abilities)."""
        import time, random
        troops = style.get("troops", {})
        corners = random.sample(list(self.CORNER_ANGLES), troops.get("corners", 4))
        battle_start = time.time() # the end timer counts from the first drop (deploying takes ~25 s)

        # Spells first, on random spots inside the village
        spells = style.get("spells")
        if spells and spells.get("card") in cards:
            tap_card(spells["card"])
            for x, y in self._inside_points(ring, 11):
                if self._card_empty(cards[spells["card"]]): break
                self._tap(x, y, spread=0.01)
                self._pause(spells.get("gap", [0.15, 0.45]))
            self._deselect()

        # Troops: per_corner on each corner, one tap each, a few pixels off every time.
        # No extra taps for leftovers: once a card runs out the game selects the next card (siege, clan spell) by itself
        # The bottom corner hides under the troop bar, so it goes last, after the view is dragged up (as a player does).
        # Points are planned first: what a corner cannot take safely (hidden edge) moves to the other corners
        per_corner = troops.get("per_corner", 15)
        gap = troops.get("tap_gap", [0.06, 0.18])
        def plan_points(ring, chosen, carry=0):
            plan = {c: self._deploy_points(ring, c, per_corner + (carry if i == 0 else 0)) for i, c in enumerate(chosen)}
            short = sum(per_corner - len(p) for p in plan.values()) + carry
            for c in [c for c in self.CORNER_ANGLES if c in plan or c in ("left", "right")]:
                if short <= 0: break
                extra = self._deploy_points(ring, c, min(short, per_corner))
                plan.setdefault(c, []).extend(extra)
                short -= len(extra)
            return plan
        troop_x = cards[troops["card"]]
        def drop(points):
            # A smaller army runs out early: then the game selects the siege card and a further tap would drop it here
            for i, (x, y) in enumerate(points):
                if i % 4 == 3 and self._card_empty(troop_x): return False
                self._tap(x, y)
                self._pause(gap)
            return True
        upper = [c for c in corners if c != "bottom"]
        plan = plan_points(ring, upper)
        tap_card(troops["card"])
        left = True
        for corner in upper:
            if not drop(plan.get(corner, [])):
                left = False
                break
            self._pause(troops.get("corner_pause", [0.3, 0.9]))
        if left and "bottom" in corners:
            ring = self._show_bottom() or ring
            plan = plan_points(ring, ["bottom"])
            logger.info(f"Bottom corner: view moved up, {len(plan.get('bottom', []))} points")
            tap_card(troops["card"])
            for corner, points in plan.items():
                if not drop(points): break
        self._leftover_troops(ring, troop_x, lambda: tap_card(troops["card"]))
        self._deselect()

        def place(x_card, corner, label):
            """The card is selected: drop it near the corner, further out each time the red line refuses it."""
            for margin in (0.035, 0.06, 0.09):
                points = self._deploy_points(ring, corner, 1, margin=margin) or self._deploy_points(ring, random.choice(corners), 1, margin=margin)
                if not points: continue
                self._tap(*points[0])
                if self._wait_deployed(x_card, timeout=2.5): return True
                if self._card_empty(x_card): return True # used up (a siege machine already gone)
                logger.info(f"{label} did not land, trying further out")
            logger.warning(f"{label} could not be deployed")
            return False

        # Siege machine: its card is tapped once only; a second tap unloads it early
        siege = style.get("siege")
        siege_card = next((c for c in sorted(cards) if siege and c.startswith(siege.get("card", "-"))), None)
        if siege_card:
            if self._card_deployed(cards[siege_card]):
                logger.info("Siege already on the field, its card is not touched")
            else:
                tap_card(siege_card)
                place(cards[siege_card], random.choice(corners), "Siege")
            self._deselect()

        # Heroes from one corner, behind the troops; abilities later, each on its own random delay, only for heroes that landed
        heroes = style.get("heroes", {})
        hero_corner = random.choice(corners)
        abilities = []
        names = [h for h in heroes.get("cards", []) if h in cards]
        for name in random.sample(names, len(names)):
            if not self._card_deployed(cards[name]): # an extra tap above may have dropped it already
                tap_card(name)
                if not place(cards[name], hero_corner, name):
                    self._deselect()
                    continue
            if name in heroes.get("ability_now", []):
                time.sleep(random.uniform(0.3, 0.6)) # Royal Champion: ability right away
                self._tap(cards[name], self.CARD_Y, spread=0.006)
                logger.info(f"{name}: ability used right after the drop")
            else:
                abilities.append((time.time() + random.uniform(*heroes.get("ability_after", [8, 12])), name))
            self._pause(heroes.get("gap", [0.25, 0.7]))
        self._deselect()
        return battle_start, abilities

    def scripted_attack(self, style_name="yayma", restart=True):
        """Play an attack style on the village on screen (search screen, nothing deployed yet). Returns True when back home."""
        import time, random, cv2, datetime
        style = self.load_style(style_name)
        shots = DEBUG_DIR / "attacks" / datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        shots.mkdir(parents=True, exist_ok=True)
        def shot(name):
            cv2.imwrite(str(shots / f"{name}.png"), cv2.cvtColor(Frame_Handler.get_frame(grayscale=False), cv2.COLOR_RGB2BGR))

        for _ in range(3):
            Input_Handler.zoom(dir="out")
            time.sleep(0.4)
        time.sleep(0.6)
        frame = Frame_Handler.get_frame(grayscale=False)
        cv2.imwrite(str(shots / "start.png"), cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        ring = self._deploy_ring(frame)
        cards = self._find_cards(frame)
        logger.info(f"Attack {style_name}: cards {', '.join(sorted(cards)) or 'none'}")
        troops = style.get("troops", {})
        if ring is None or troops.get("card") not in cards:
            logger.error("Attack aborted: deploy line or troop card not found")
            self._leave_search() # nothing deployed yet, so this costs nothing
            return False

        def tap_card(name):
            self._tap(cards[name], self.CARD_Y, spread=0.006)
            time.sleep(random.uniform(0.08, 0.2))

        if troops.get("mode") == "drag": # Emre's spread attack (attacks/yayma.yaml)
            battle_start, abilities = self._deploy_spread(style, ring, cards, shots)
        else:
            battle_start, abilities = self._deploy_corners(style, ring, cards, tap_card)
        shot("deployed")

        # Battle: abilities on time, end when the loot stops moving, then Return Home
        end = style.get("end", {})
        end_factor = random.uniform(*end.get("after_factor", [1, 1])) # not the same second every battle
        # Emre 23:04: once the gold and elixir left in the village are both under ~50-70 k, leave at once
        loot_floor = random.uniform(*end["loot_left"]) if end.get("loot_left") else 0
        start, last_change, last_loot, n = time.time(), time.time(), None, 0
        while time.time() - start < end.get("max_seconds", 180):
            for due, name in sorted(abilities):
                if time.time() >= due:
                    self._tap(cards[name], self.CARD_Y, spread=0.006)
                    abilities.remove((due, name))
            if self._click_button("return_home", timeout=0.3):
                break
            end_after = round((Settings_Handler.get("attack", "end_after", 60) or 0) * end_factor)
            timed_out = end_after > 0 and time.time() - battle_start >= end_after
            loot_gone = False
            if not timed_out: # reading the loot takes ~3 s, not needed once the time is up
                loot, _ = self._read_loot()
                if None not in loot.values() and loot != last_loot: last_loot, last_change = loot, time.time()
                loot_gone = loot_floor > 0 and None not in (loot["gold"], loot["elixir"]) and max(loot["gold"], loot["elixir"]) < loot_floor
            if loot_gone or ((time.time() - last_change >= end.get("idle_seconds", 20) or timed_out) and not abilities):
                if loot_gone: logger.info(f"Loot left under {int(loot_floor):,}, ending the battle".replace(",", "."))
                elif timed_out: logger.info(f"{end_after}s after the first drop, ending the battle")
                else: logger.info(f"Loot unchanged for {end.get('idle_seconds', 20)}s, ending the battle")
                if self._click_button("surrender", timeout=2) or self._click_button("end_battle", timeout=2):
                    time.sleep(1)
                    shot("end_dialog")
                    if not self._click_button("okay", timeout=3):
                        logger.warning("Okay not found on the end battle dialog, waiting for the battle to end")
                break
            n += 1
            if n % 3 == 0: shot(f"battle_{n:03d}")
            time.sleep(1.5)

        # Results screen: Return Home (screenshots kept until its picture is measured on this UI)
        start = time.time()
        while time.time() - start < 60:
            shot(f"result_{int(time.time() - start):02d}")
            # The village takes a few seconds to load after Return Home (clouds): wait for it instead of looking again
            pressed = self._click_button("return_home", timeout=1)
            for _ in range(15 if pressed else 1):
                if in_home_base():
                    TEMP_CACHE["location"] = "home_base"
                    logger.info("Battle over, back home")
                    return True
                time.sleep(1)
        logger.warning("Return Home not found, restarting CoC instead")
        if restart: start_coc()
        else: stop_coc()
        return False

    # ============================================================
    # 🔍 Search
    # ============================================================

    # Available loot on the search screen (x1, y1, x2, y2), measured at 1920x1080
    LOOT_REGIONS = {
        "gold": (0.050, 0.118, 0.160, 0.165),
        "elixir": (0.050, 0.172, 0.160, 0.220),
        "dark": (0.050, 0.225, 0.160, 0.272),
    }

    @staticmethod
    def _tap(x, y, spread=0.004):
        import random
        # A few pixels off every time, like a finger
        Input_Handler.click(x + random.uniform(-spread, spread), y + random.uniform(-spread, spread))

    def _click_battle(self):
        # The shop's pack price buttons sit exactly where Battle is; only tap it when it is really there
        if not in_home_base(): return False
        x, y = Frame_Handler.locate(self.assets["battle"], grayscale=False, thresh=0.97)
        if x is None or x > 0.15 or y < 0.85: return False
        self._tap(x, y)
        return True

    def _wait_village(self, timeout=30):
        import time
        # The Next button shows up once the clouds are gone and the loot is on screen
        start_time = time.time()
        while time.time() - start_time < timeout:
            x, y = Frame_Handler.locate(self.assets["next"], grayscale=False, thresh=0.9)
            if x is not None: return x, y
            time.sleep(0.2)
        return None

    def _read_loot(self):
        import re
        frame = Frame_Handler.get_frame(grayscale=False)
        loot = {}
        for name, region in self.LOOT_REGIONS.items():
            digits = re.sub(r"\D", "", OCR_Handler.read_digits(Frame_Handler.crop(frame, *region)))
            loot[name] = int(digits) if digits else None
        return loot, frame

    @staticmethod
    def loot_minimums(attack, n):
        # Every `lower_every` searches the minimums drop by `lower_pct` % of the panel value
        every, pct = attack.get("lower_every", 0) or 0, attack.get("lower_pct", 0) or 0
        steps = (n - 1) // every if every > 0 else 0
        factor = max(0.0, 1 - steps * pct / 100)
        return {k: int((attack.get(f"min_{k}", 0) or 0) * factor) for k in ("gold", "elixir", "dark")}

    @staticmethod
    def loot_ok(loot, mins):
        # Every non-zero minimum has to hold; 0 means no condition, an unreadable value fails it
        return all(m <= 0 or (loot.get(k) or 0) >= m for k, m in mins.items())

    def _leave_search(self, timeout=20):
        import time
        # No troops deployed yet, so End Battle goes straight home and costs nothing
        if not self._click_end_battle(timeout=5):
            logger.error("End Battle not found on the search screen")
            return False
        start_time = time.time()
        while time.time() - start_time < timeout:
            if in_home_base():
                TEMP_CACHE["location"] = "home_base"
                return True
            time.sleep(0.5)
        logger.error("Did not get back home from the search screen")
        return False

    def _save_village(self, frame, n):
        import cv2, datetime
        # Kept for building templates (dark elixir drills); debug/ is not committed
        folder = DEBUG_DIR / "villages"
        folder.mkdir(parents=True, exist_ok=True)
        name = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{n:02d}.png"
        cv2.imwrite(str(folder / name), cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

    def search(self, attack, search_only=False):
        """Next through villages until the loot minimums hold.
        Returns the loot of the chosen village (still on its screen unless search_only), or None when back home."""
        import time, random

        if not self._open_search(): return None
        max_searches = max(1, int(attack.get("max_searches", 30) or 30))
        fmt = lambda v: "-" if v is None else f"{v:,}".replace(",", ".")
        for n in range(1, max_searches + 1):
            if self._wait_village() is None:
                logger.error("Village did not load")
                self._leave_search()
                return None
            time.sleep(0.5)
            loot, frame = self._read_loot()
            # OCR sometimes adds a digit (an iksir of 1.037.617 read as 10.376.176): keep values two reads agree on
            second, _ = self._read_loot()
            if second != loot:
                third, _ = self._read_loot()
                loot = {k: loot[k] if loot[k] in (second[k], third[k]) else second[k] if second[k] == third[k] else None for k in loot}
            if search_only or attack.get("save_villages"): self._save_village(frame, n)
            mins = self.loot_minimums(attack, n)
            logger.info(
                f"Search {n}: gold={fmt(loot['gold'])} elixir={fmt(loot['elixir'])} dark={fmt(loot['dark'])} "
                f"min={fmt(mins['gold'])}/{fmt(mins['elixir'])}/{fmt(mins['dark'])}"
            )
            if self.loot_ok(loot, mins):
                logger.info(f"Village found after {n} searches")
                if search_only: self._leave_search()
                return loot
            if n == max_searches: break
            # Look at the village for a moment, but decide well inside the 30 s scouting time
            time.sleep(random.uniform(1.5, 4.0))
            xy = self._wait_village(timeout=2)
            if xy is None:
                logger.error("Next button not found")
                self._leave_search()
                return None
            self._tap(*xy)
            time.sleep(1)
        logger.info(f"No village in {max_searches} searches, trying again next round")
        self._leave_search()
        return None

    @require_exit()
    def run_search_only(self, timeout=10):
        import time

        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                if in_home_base(): break
            if time.time() - start_time >= timeout:
                logger.error("Not in home base. Aborting search.")
                return
            self.search(Settings_Handler.get_section("attack"), search_only=True)
        except Exception:
            logger.exception("Error in run_search_only():")

    def _open_search(self):
        import numpy as np

        if not self._click_battle():
            logger.error("Battle button not found")
            return False

        # Find a match
        find_a_match_temp = render_text("Find a Match", "SupercellMagic", 29)
        battle_temp = render_text("Battle", "SupercellMagic", 37)
        def locate_find_a_match():
            frame = Frame_Handler.get_frame(grayscale=True, high_contrast=True)
            bx, by = Frame_Handler.locate(battle_temp, frame, thresh=0.9)
            if bx is None or by is None: return None, None
            xys = Frame_Handler.locate(find_a_match_temp, frame, thresh=0.9, return_all=True)
            xys = [p for p in xys if p[0] is not None and p[1] is not None] # matches can come mixed with empty ones (20:46)
            if not xys: return None, None
            xys = np.array(xys, dtype=float)
            dists = abs(xys[:, 0] - bx)
            if min(dists) > 0.01: return None, None
            x, y = xys[np.argmin(dists)]
            if x is None or y is None: return None, None
            return x, y
        if not click_with_timeout(
            locate_find_a_match,
            timeout=5
        ):
            logger.error("Failed to click find a match button")
            return False

        # Confirm attack (the army window can take a few seconds to open)
        if not click_with_timeout(
            lambda: Frame_Handler.locate(self.assets["confirm_attack"], thresh=0.9),
            timeout=10
        ):
            logger.error("Failed to confirm attack")
            return False
        return True
    
    def start_builder_attack(self, timeout=60):
        import time
        
        # Click attack
        Input_Handler.click(0.07, 0.9)
        
        # Find a match
        if not click_with_timeout(
            lambda: Frame_Handler.locate(self.assets["find_now"], thresh=0.9),
            timeout=5
        ): return False
        
        # Wait until "battle starts in" text is found
        start_time = time.time()
        while time.time() - start_time < timeout:
            section = Frame_Handler.get_frame_section(0, 0, 1, 0.1, grayscale=True, high_contrast=True, thresh=150)
            x, y = Frame_Handler.locate(self.assets["battle_starts_in"], section, thresh=0.9)
            if x is not None and y is not None: return True
            time.sleep(0.1)
        return False
    
    def detect_troop_positions(self, frame, clip_left=0.0, clip_right=1.0, type_gaps_seen=0, return_boundaries=False, return_types=False, return_counts=False):
        import cv2, scipy, numpy as np
        
        # Look for vertical card edges
        assert len(frame.shape) == 3 and frame.shape[2] == 3
        frame_color = frame.copy()
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        orig_h, orig_w = frame_gray.shape
        frame_color = frame_color[:, max(0, int(orig_w*clip_left)-10):min(orig_w, int(orig_w*clip_right)+10)]
        frame_gray = frame_gray[:, max(0, int(orig_w*clip_left)-10):min(orig_w, int(orig_w*clip_right)+10)]
        frame_gray = cv2.equalizeHist(frame_gray)
        edges = cv2.convertScaleAbs(np.abs(cv2.Sobel(frame_gray, cv2.CV_64F, 1, 0, ksize=3)))
        profile = np.sum(edges, axis=0)
        profile = (profile - profile.min()) / (profile.max() - profile.min())
        peaks = scipy.signal.find_peaks(profile, height=0.8, distance=10)[0]
        peaks_norm =  peaks / orig_w + clip_left
        
        # Compute distances between edges and discretize
        dists = np.diff(peaks_norm)
        dist_categories = np.array([0.007, 0.015, 0.068]) # normal gap, type change gap, card width
        tol = 0.01
        diffs = np.abs(dists[:, None] - dist_categories)
        closest_idx = np.argmin(diffs, axis=1)
        closest_dist = diffs[np.arange(len(dists)), closest_idx]
        dists_discrete = dist_categories[closest_idx]
        dists_discrete[closest_dist > tol] = np.nan
        
        # Remove partially visible card edges
        remove_left = 0
        remove_right = len(dists_discrete) - 1
        while dists_discrete[remove_left] != dist_categories[2]: remove_left += 1
        while dists_discrete[remove_right] != dist_categories[2]: remove_right -= 1
        peaks = peaks[remove_left:remove_right+2]
        peaks_norm = peaks_norm[remove_left:remove_right+2]
        dists_discrete = dists_discrete[remove_left:remove_right+1]
        
        assert len(peaks) % 2 == 0, "Uneven number of troop slot edges detected"
        
        # Convert edge distances to card locations
        card_types = []
        card_centers = []
        card_boundaries = []
        card_counts = []
        for i in range(0, len(peaks_norm), 2):
            x = (peaks_norm[i] + peaks_norm[i+1]) / 2
            card_centers.append(x)
            card_boundaries.extend([peaks_norm[i], peaks_norm[i+1]])
            prev_gap = dists_discrete[i-1] if i-1 > 0 else dist_categories[0]
            next_gap = dists_discrete[i+1] if i+1 < len(dists_discrete) else dist_categories[0]
            if prev_gap == dist_categories[1]: type_gaps_seen += 1
            
            # Figure out whether card is a normal troop, clan troop, or hero
            card_section = frame_color[:, peaks[i]:peaks[i+1]]
            card_section_gray = frame_gray[:, peaks[i]:peaks[i+1]]
            h, w = card_section_gray.shape[:2]
            card_texture = cv2.Canny(card_section_gray, 50, 150) / 255
            x_asset = render_text("x", "SupercellMagic", 25)
            x_h, x_w = x_asset.shape[:2]
            x_sign_loc = Frame_Handler.locate(x_asset, card_section_gray, grayscale=True, thresh=0.75, ref="lc")
            if x_sign_loc[0] is not None and x_sign_loc[1] is not None: # Only troops, clan troops, or spells have multiplicity
                count_section = card_section_gray[:int(h*x_sign_loc[1]+0.5*x_h)+1, int(w*x_sign_loc[0]+x_w)-1:]
                number_locs = Frame_Handler.batch_locate([render_text(str(n), "SupercellMagic", 25) for n in range(0, 12)], frame=count_section, grayscale=True, thresh=0.8, ref="cc")
                
                count = 1
                for i in reversed(range(0, 12)):
                    loc = number_locs[i]
                    if loc[0] is not None and loc[1] is not None:
                        count = i
                        break
                
                # Clan troops either have a clan badge rather than a smooth background
                # or will have wider card edge gaps compared to typical troops
                if max(card_texture[int(h*x_sign_loc[1])-10:int(h*x_sign_loc[1])+10, :int(w*x_sign_loc[0]-1)].mean(1)) > 0.1:
                    card_type = "clan"
                    card_counts.append(1)
                elif prev_gap == dist_categories[1] and next_gap == dist_categories[1]:
                    card_type = "clan"
                    card_counts.append(1)
                elif type_gaps_seen > 0:
                    card_type = "spell"
                    card_counts.append(count)
                else:
                    card_type = "troop"
                    card_counts.append(-1)
            else:
                card_section_border = card_section.copy()
                card_section_border[int(h*0.1):int(h*0.9), int(w*0.1):int(w*0.9)] = 0
                mask = filter_color((68, 202, 222), card_section_border, tol=100, return_mask=True)[1]
                blue_pct = mask.mean()
                # Seige machine doesn't have multiplicity anymore
                if blue_pct > 0.1:
                    card_type = "clan"
                    card_counts.append(1)
                else:
                    card_type = "hero"
                    card_counts.append(1)
            card_types.append(card_type)

        card_centers = np.array(card_centers)
        
        if not return_boundaries and not return_types: return card_centers
        
        output = [card_centers]
        if return_boundaries: output.append(card_boundaries)
        if return_types: output.append(card_types)
        if return_counts: output.append(card_counts)
        output.append(type_gaps_seen)
        return output
    
    def deploy_troops(self, card_centers, available_slots=None, card_types=None, card_counts=None):
        import time, numpy as np
        
        def card_gray(card_center):
            section = Frame_Handler.get_frame_section(card_center-0.01, 0.89, card_center+0.01, 0.91, grayscale=False)
            return np.all(section[:, :, 0] == section[:, :, 1]) and np.all(section[:, :, 1] == section[:, :, 2])
        
        if available_slots is None: available_slots = [1] * len(card_centers)
        if card_types is None: card_types = [None] * len(card_centers)
        if card_counts is None: card_counts = [0] * len(card_centers)
        
        # Start holding deploy position w/ additional touch pointer
        Input_Handler.down(0.5, 0.8, pointer=1)
        
        for i in range(len(card_centers)):
            if available_slots[i]:
                # Select slot
                Input_Handler.click(card_centers[i], 0.9)
                
                # Deploy selected slot
                if card_types[i] in ["hero", "clan"]:
                    Input_Handler.click(0.5, 0.8)
                elif card_types[i] == "troop":
                    Input_Handler.down(0.5, 0.8, pointer=0)
                    end_time = time.monotonic() + TROOP_DEPLOY_TIME
                    while time.monotonic() < end_time and not card_gray(card_centers[i]): time.sleep(0.01)
                    Input_Handler.up(pointer=0)
                elif card_types[i] == "spell":
                    n = card_counts[i]
                    rxs = np.random.uniform(0.35, 0.65, n)
                    rys = np.random.uniform(0.45, 0.55, n)
                    for coord in zip(rxs, rys):
                        Input_Handler.click(*coord)
                else:
                    Input_Handler.click(0.5, 0.8, n=max(0, card_counts[i]))
        
        # Release additional pointer
        Input_Handler.up(pointer=1)
        
        # Unselect last card
        Input_Handler.click(0.01, 0.9)
    
    def complete_normal_attack(self, restart=True, exclude_clan_troops=False):
        import time, numpy as np

        Input_Handler.zoom(dir="out")
        Input_Handler.swipe_up(y1=0.5)
        
        type_gaps_seen = 0
        total_slots_seen = 0
        last_card_left = 0.0
        
        while total_slots_seen < ATTACK_SLOT_RANGE[1] - ATTACK_SLOT_RANGE[0] + 1:
            frame = Frame_Handler.get_frame_section(0.0, 0.82, 1.0, 1.0, grayscale=False)
            # Find troops to deploy
            card_centers, card_boundaries, card_types, card_counts, type_gaps_seen = self.detect_troop_positions(frame, clip_left=last_card_left, type_gaps_seen=type_gaps_seen, return_boundaries=True, return_types=True, return_counts=True)

            if len(card_centers) == 0: break

            # Exclude clan troops if specified
            available_slots = np.ones_like(card_centers)
            if exclude_clan_troops:
                for i, card_type in enumerate(card_types):
                    if card_type == "clan": available_slots[i] = 0
            
            # Exclude troops outside of specified slot range
            available_slots[:max(0, ATTACK_SLOT_RANGE[0] - total_slots_seen)] = 0
            available_slots[max(0, ATTACK_SLOT_RANGE[1] + 1 - total_slots_seen):] = 0
            
            # Deploy troops up until the last one visible
            total_slots_seen += len(card_centers) - 1
            self.deploy_troops(card_centers[:-1], available_slots[:-1], card_types[:-1], card_counts[:-1])
            # Scroll over and look for the new position of the last card
            last_card_frame = frame[:, int(card_boundaries[-2] * frame.shape[1]):int(card_boundaries[-1] * frame.shape[1])]
            Input_Handler.swipe_left(x1=card_centers[-1], x2=0.038, y=0.9, hold_end_time=500)
            time.sleep(0.5)
            frame = Frame_Handler.get_frame_section(0.0, 0.82, 1.0, 1.0, grayscale=False)
            last_card_left = Frame_Handler.locate(last_card_frame, frame, thresh=0.9, grayscale=False, ref="lc")[0]
            # If the card didn't move then there are no more troops so it can be deployed
            if last_card_left is not None and abs(last_card_left - card_boundaries[-2]) < 0.01:
                self.deploy_troops(card_centers[-1:], available_slots[-1:], card_types[-1:], card_counts[-1:])
                break
            elif last_card_left is None:
                break

        if getattr(configs, "WAIT_FOR_BATTLE_END", True) and self._wait_battle_end("home_base", timeout=210):
            if not restart: stop_coc()
            return

        # Close and reopen CoC to auto complete battle
        if restart:
            start_coc()
        else:
            stop_coc()
    
    def complete_builder_attack(self, restart=True):
        import numpy as np
        
        Input_Handler.zoom(dir="out")
        Input_Handler.swipe_up(y1=0.5)
        
        card_centers = np.linspace(0.1, 0.9, 11)
        self.deploy_troops(card_centers, card_counts=[4]*len(card_centers))

        # builder battles can run two stages, so allow longer before falling back
        if getattr(configs, "WAIT_FOR_BATTLE_END", True) and self._wait_battle_end("builder_base", timeout=300):
            if not restart: stop_coc()
            return

        # Close and reopen CoC to auto complete battle
        if restart:
            start_coc()
        else:
            stop_coc()
    
    # ============================================================
    # ⚔️ Attack Management
    # ============================================================

    @require_exit()
    def run_home_base(self, timeout=10, restart=True):
        import time
        
        try:
            # Make sure in home base
            start_time = time.time()
            while time.time() - start_time < timeout:
                if in_home_base(): break
            if time.time() - start_time >= timeout:
                logger.error("Not in home base. Aborting home attack.")
                return
            
            # Find a village worth attacking, then attack it
            if self.search(Settings_Handler.get_section("attack")) is not None:
                self.scripted_attack("yayma", restart=restart)
            elif not in_home_base():
                start_coc() # reset in case stuck on find a match screen
        
        except Exception:
            logger.exception("Error in run_home_base():")

    @require_exit()
    def run_builder_base(self, timeout=10, restart=True):
        import time
        
        try:
            # Make sure in builder base
            start_time = time.time()
            while time.time() - start_time < timeout:
                if in_builder_base(): break
            if time.time() - start_time >= timeout:
                logger.error("Not in builder base. Aborting builder attack.")
                return
            
            # Complete an attack
            if self.start_builder_attack(timeout):
                self.complete_builder_attack(restart=restart)
            else:
                start_coc() # reset in case stuck on find a match screen
        
        except Exception:
            logger.exception("Error in run_builder_base():")
