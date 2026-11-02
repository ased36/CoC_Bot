from utils import *
try:
    import configs
    from configs import *
except:
    import configs_build as configs
    from configs_build import *

class Upgrader:
    def __init__(self):
        self.assets = Asset_Manager.upgrader_assets
        self.misc_assets = Asset_Manager.misc_assets
        self.dry_run = False # choose and open the upgrade, but do not confirm (testing)

    # Menus that need not be opened every round (Emre 02.11: a busy pet house, an apprentice already used): the next
    # look is kept in the disk cache, so closing and opening the bot keeps it
    @staticmethod
    def _due(key):
        import time
        return time.time() >= (Cache_Manager.get("look_again") or {}).get(key, 0)

    @staticmethod
    def _later(key, hours, why):
        import time
        from datetime import datetime
        at = time.time() + hours * 3600
        Cache_Manager["look_again"] = dict(Cache_Manager.get("look_again") or {}, **{key: at})
        logger.info(f"{why}, next look at {datetime.fromtimestamp(at).strftime('%d.%m %H:%M')}")

    def _paid(self, before, name):
        """The chosen row's cost really left the storage. 02.11 04:23 and 04:29 the pet house read busy after the confirm
        tap, but no dark elixir was spent: the upgrade had not started (and Telegram said it had)."""
        resource, cost = getattr(self, "last_choice", None) or (None, None)
        after = (Resource_Reader.read() or {}).get(resource)
        if not cost or before.get(resource) is None or after is None: return True # cannot tell, trust the count
        if after <= before[resource] - cost * 0.5: return True
        n = lambda v: f"{v:,}".replace(",", ".")
        logger.warning(f"{name}: {resource} did not drop ({n(before[resource])} -> {n(after)}, cost {n(cost)}), not started")
        Frame_Handler.save_frame(Frame_Handler.get_frame(grayscale=False), "not_started.png")
        return False

    # ============================================================
    # 👷 Builder status (Emre 02.11): the ongoing upgrades on top of the builders and laboratory menus, with the time
    # left at the right of each row ("6H 29M", "1d 5H"); measured on the 02.11 04:58 frames
    # ============================================================

    TIME_UNITS = {"D": 86400, "H": 3600, "M": 60, "S": 1}
    TIME_LIMITS = {"D": 99, "H": 23, "M": 59, "S": 59}

    @classmethod
    def parse_time(cls, text):
        """Game time text -> (seconds, precision): the second unit shown is the precision ("1d 5H" = 1 day 5 hours, up to
        an hour more). OCR slips seen 02.11: the H read as a 4 ("64 29M"), a 5 as S ("1d SH"), a 2 as Z. None = not a time."""
        import re
        order = "DHMS"
        s = text.upper().replace("O", "0").replace("I", "1").replace("L", "1").replace("Z", "2").replace("B", "8")
        s = re.sub(r"S(?=[\dDHM])", "5", s)
        tokens = ["11M" if t == "MM" else t for t in s.split()] # "11M": the two thin 1s read as one M (02.11 05:13 "4H MM")
        if not 1 <= len(tokens) <= 2: return None
        parts = []
        for tok in tokens:
            m = re.fullmatch(r"(\d+)([DHMS]?)", tok)
            if not m: return None
            parts.append([m.group(1), m.group(2)])
        if len(parts) == 2: # a unit lost to OCR comes from the order
            (_, u1), (_, u2) = parts
            if not u1 and u2 and order.index(u2) > 0: parts[0][1] = order[order.index(u2) - 1]
            if u1 and not u2 and order.index(u1) < 3: parts[1][1] = order[order.index(u1) + 1]
        total, last = 0, -1
        for digits, unit in parts:
            if not unit: return None
            v = int(digits)
            if v > cls.TIME_LIMITS[unit] and len(digits) > 1 and digits[-1] == "4": v = int(digits[:-1]) # "164": 16 and the H
            if v > cls.TIME_LIMITS[unit] or order.index(unit) <= last or (last >= 0 and order.index(unit) != last + 1): return None
            last = order.index(unit)
            total += v * cls.TIME_UNITS[unit]
        return total, cls.TIME_UNITS[order[last]]

    def _read_time(self, section):
        """Three readings of a white time text (two masks and the picture itself), the most common valid one."""
        import cv2, numpy as np, collections
        OCR_Handler.load()
        reads = []
        for mask in (section.min(axis=2) > 200, section.min(axis=2) > 170):
            m = cv2.copyMakeBorder(255 - mask.astype(np.uint8) * 255, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=255)
            reads.append(m)
        reads.append(section)
        texts = [" ".join(OCR_Handler.reader.readtext(cv2.resize(r, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC), detail=0,
                                                       allowlist="0123456789dhmsDHMS ")) for r in reads]
        # The picture once more with I and l allowed: thin 1s come out as I ("4H IIm" = 4H 11M), parse_time makes them 1
        texts.append(" ".join(OCR_Handler.reader.readtext(cv2.resize(section, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC), detail=0,
                                                          allowlist="0123456789dhmsDHMSIl ")))
        valid = [v for v in map(self.parse_time, texts) if v is not None]
        return collections.Counter(valid).most_common(1)[0][0] if valid else None

    def _read_ongoing(self, frame):
        """[(name, seconds left, precision)] of the rows above "Suggested upgrades" / "Other upgrades" in an open builders
        or laboratory menu (1920x1080: names from x 1426, times x 1790-1892, rows ~58 px apart)."""
        import re, difflib
        OCR_Handler.load()
        crop = frame[60:1000, 1400:1920]
        boxes = [(int((b[0][1] + b[2][1]) / 2) + 60, int(b[0][0]) + 1400, t) for b, t, _ in OCR_Handler.reader.readtext(crop, detail=1)]
        stop = min([y for y, _, t in boxes if re.search(r"sugg|other\s*upg", t, re.I)] or [1000])
        rows = []
        for y, x, t in sorted(boxes):
            if x > 1700 or not 80 < y < stop - 20: continue
            if rows and abs(rows[-1][0] - y) < 14: rows[-1][1] += " " + t # one name in two boxes
            else: rows.append([y, t])
        names = Cache_Manager.get("vocab") or {}
        names = [n for v in names.values() for n in v]
        out = []
        for y, text in rows:
            left = self._read_time(frame[max(0, y - 20):y + 20, 1790:1892])
            if left is None: continue
            raw = re.sub(r"\s*x\s*\d+$", "", text.strip(), flags=re.I).title()
            name = (difflib.get_close_matches(raw, names, 1, 0.6) or [raw])[0]
            out.append((name, left[0], left[1]))
        return out

    # A running potion shows its time left in a dark box with the bottle at its right, left of the open menu (02.11: builder
    # potion = blue bottle with a hammer, "53m 49s" at 05:13; research potion = purple bottle, "8m 8s" at 04:58)
    POTION_BOX = (1120, 540, 1420, 650) # x1, y1, x2, y2 on 1920x1080
    POTION_SPEED = {"builders": 10, "lab": 24} # builder potion 10x (Emre; 05:13-05:16 measured ~10), research potion 24x

    def _read_potion(self, frame):
        """(kind "builders" / "lab", seconds left) of the potion box on screen, or None."""
        import re
        OCR_Handler.load()
        x1, y1, x2, y2 = self.POTION_BOX
        for box, text, _ in OCR_Handler.reader.readtext(frame[y1:y2, x1:x2], detail=1, allowlist="0123456789dhmsDHMSIl "):
            if not re.search(r"[MmSs]\s*$", text.strip()): continue # a potion counts minutes and seconds
            bx1, by1 = int(box[0][0]) + x1, int(box[0][1]) + y1
            bx2, by2 = int(box[2][0]) + x1, int(box[2][1]) + y1
            left = self._read_time(frame[max(0, by1 - 4):by2 + 4, max(0, bx1 - 4):bx2 + 4]) or self.parse_time(text)
            if not left: continue
            bottle = frame[by1:by2, bx2:min(frame.shape[1], bx2 + 90)].reshape(-1, 3).astype(int)
            r, g, b = bottle[:, 0], bottle[:, 1], bottle[:, 2]
            blue = ((b > 170) & (b - r > 60) & (g > 120)).sum() # builder potion ~ (82, 172, 195)
            purple = ((r > 100) & (b > 70) & (g < 60) & (r - g > 60)).sum() # research potion ~ (143, 5, 100)
            if max(blue, purple) < 30: continue # no bottle next to it: not a potion box
            return ("builders" if blue >= purple else "lab"), left[0]
        return None

    @staticmethod
    def boosted_left(left, potion_left, speed):
        """Real time to the end: while the potion runs every minute does speed minutes of work (Emre 02.11: 10 hours of
        work with a builder potion end in 1 hour), the rest at normal speed."""
        if potion_left <= 0: return left
        if left <= potion_left * speed: return left / speed
        return potion_left + left - potion_left * speed

    @require_exit(x=0.99, y=0.01)
    def _status_menu(self, kind):
        import time
        self._click_build_button()
        time.sleep(0.5)
        {"builders": self._click_home_builders, "lab": self._click_home_lab}[kind]()
        time.sleep(1.0)
        frame = Frame_Handler.get_frame(grayscale=False)
        Frame_Handler.save_frame(frame, f"menu_{kind}_top.png")
        return self._read_ongoing(frame), self._read_potion(frame)

    def read_status(self):
        """Builders and laboratory: what is being upgraded and when it ends, into the disk cache (Telegram /ozet, the
        panel's Ustalar card). "left" is the work the menu shows; "end" is when it really ends, with a running potion
        (builder 10x, research 24x) counted in; "prec" is how much later it can be (the time shown is rounded down)."""
        import time
        status = dict(Cache_Manager.get("status") or {})
        status["t"] = now = time.time()
        for kind in ("builders", "lab"):
            try:
                read = self._status_menu(kind)
            except (KeyboardInterrupt, SystemExit): raise
            except Exception:
                logger.exception(f"Upgrader.read_status({kind}):")
                continue
            if read is None: continue
            rows, potion = read
            # The box shows the potion of the open menu; a bottle of the other kind is not this menu's
            potion_left = potion[1] if potion and potion[0] == kind else 0
            speed = self.POTION_SPEED[kind]
            status[f"{kind}_potion"] = {"end": now + potion_left, "speed": speed} if potion_left else None
            status[kind] = [{"name": n, "left": s, "end": now + self.boosted_left(s, potion_left, speed),
                             "prec": p / speed if potion_left and s <= potion_left * speed else p} for n, s, p in rows]
            boost = f" (potion {self.fmt_left(potion_left)} left, x{speed})" if potion_left else ""
            logger.info(f"Status {kind}{boost}: " + (", ".join(f"{n} {self.fmt_left(s)}" for n, s, _ in rows) or "nothing running"))
        Cache_Manager["status"] = status
        report("status", status=status)
        return status

    @staticmethod
    def fmt_left(seconds):
        d, r = divmod(int(seconds), 86400)
        h, r = divmod(r, 3600)
        return f"{d}d {h}h" if d else f"{h}h {r // 60}m" if h else f"{r // 60}m"

    # ============================================================
    # 📱 Screen Interaction
    # ============================================================
    
    def _click_build_button(self):
        Input_Handler.click(0.95, -0.05)
    
    def _click_home_builders(self):
        Input_Handler.click(0.77, -0.05)
    
    def _click_home_lab(self):
        Input_Handler.click(0.84, -0.05)
    
    def _click_pet_house(self):
        Input_Handler.click(0.97, -0.05)

    def _click_builder_builders(self):
        Input_Handler.click(0.8, -0.05)
    
    def _click_builder_lab(self):
        Input_Handler.click(0.94, -0.05)

    def _click_upgrade(self, timeout=5):
        import cv2, numpy as np
        scale_templates = []
        for scale in np.arange(0.9, 1.1, 0.1):
            scale_templates.append(cv2.resize(self.assets["upgrade"], (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST))
        
        def locate():
            xys = Frame_Handler.batch_locate(scale_templates, thresh=0.90, grayscale=False)
            for x, y in xys:
                if x is None or y is None: continue
                return x, y
            return None, None

        return click_with_timeout(locate, timeout=timeout)

    def _click_home_confirm(self, timeout=5):
        # A fresh frame on every try: the cached one was taken before the dialog opened, so Confirm was never seen
        return click_with_timeout(
            lambda: Frame_Handler.locate(self.assets["confirm"], grayscale=False, thresh=0.85),
            timeout=timeout
        )

    @staticmethod
    def _find_green_button(frame, region, word):
        """Center of the biggest green button in region whose text starts with word (OCR), or (None, None)."""
        import cv2, numpy as np
        x1, y1, x2, y2 = region
        h, w = frame.shape[:2]
        sec = Frame_Handler.crop(frame, x1, y1, x2, y2).astype(int)
        green = (sec[..., 1] > 170) & (sec[..., 1] - sec[..., 2] > 60) & (sec[..., 0] < 210)
        n, _, stats, _ = cv2.connectedComponentsWithStats(green.astype(np.uint8))
        if n < 2: return None, None
        i = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        bx, by, bw, bh, area = stats[i]
        if area < 5000: return None, None
        left, top = x1 + bx / w, y1 + by / h
        texts = OCR_Handler.get_text(Frame_Handler.crop(frame, left, top, left + bw / w, top + bh / h))
        if not any(t.lower().replace(" ", "").startswith(word) for t in texts): return None, None
        return left + bw / w / 2, top + bh / h / 2

    def _click_walls_confirm(self, timeout=5):
        """Several walls at once ask "Upgrade Walls … Cancel / Okay" instead of the Confirm dialog of one wall."""
        import time
        start = time.time()
        while time.time() - start < timeout:
            frame = Frame_Handler.get_frame(grayscale=False)
            x, y = self._find_green_button(frame, (0.50, 0.52, 0.75, 0.76), "ok")
            # The "Confirm Exit" (quit the game) dialog has the same Okay in the same place: check the title
            title = " ".join(OCR_Handler.get_text(Frame_Handler.crop(frame, 0.30, 0.24, 0.70, 0.37))).lower() if x is not None else ""
            if x is not None and "upgrade" in title and "confirm" not in title: # OCR: "Upgrade Walis", "Confirm Exxit"
                Input_Handler.click(x, y)
                return True
            time.sleep(0.4)
        return False

    def _click_builder_confirm(self, timeout=5):
        return click_with_timeout(
            lambda: self._find_builder_confirm(),
            timeout=timeout
        )

    def _scroll_to_menu_bottom(self, menu_left, menu_right, menu_top, menu_bottom, max_scrolls=10):
        import numpy as np
        menu_center = (menu_left + menu_right) / 2
        for _ in range(max_scrolls):
            menu_prev = Frame_Handler.get_frame_section(menu_left, menu_top, menu_right, menu_bottom, high_contrast=True)
            Input_Handler.swipe_up(x=menu_center, y1=menu_bottom-0.05, y2=menu_top, duration=0, hold_end_time=0)
            menu_curr = Frame_Handler.get_frame_section(menu_left, menu_top, menu_right, menu_bottom, high_contrast=True)
            diff = np.abs(menu_curr - menu_prev).mean() / 255
            if diff < 0.01: break

    # ============================================================
    # 💰 Resource & Builder Tracking
    # ============================================================
    
    def get_home_builders(self, timeout=60, use_cached_frame=False):
            import time
            
            start = time.time()
            while time.time() < start + timeout:
                try:
                    section = Frame_Handler.get_frame_section(0.89, 0.75, -0.07, -0.21, high_contrast=True, use_cached=use_cached_frame)
                    if configs.DEBUG: Frame_Handler.save_frame(section, "home_builders.png")
                    
                    slash = render_text("/", "SupercellMagic", 24)
                    x, y, c = Frame_Handler.locate(
                        slash,
                        section,
                        grayscale=True,
                        return_confidence=True
                    )
                    if c < 0.9: continue
                    
                    text = fix_digits(''.join(OCR_Handler.get_text(section)).replace(' ', '').replace('/', ''))
                    available = int(text[0])
                    return available
                except (KeyboardInterrupt, SystemExit): raise
                except Exception as e:
                    logger.error(f"Upgrader.get_home_builders: {e}")
                time.sleep(0.5)
            logger.error("Upgrader.get_home_builders: Failed to get home builders")
            raise Exception("Failed to get home builders")
    
    def get_builder_builders(self, timeout=60, use_cached_frame=False):
        import time
        
        start = time.time()
        while time.time() < start + timeout:
            try:
                section = Frame_Handler.get_frame_section(0.89, 0.75, -0.07, -0.21, high_contrast=True, use_cached=use_cached_frame)
                if configs.DEBUG: Frame_Handler.save_frame(section, "builder_builders.png")
                
                slash = render_text("/", "SupercellMagic", 24)
                x, y, c = Frame_Handler.locate(
                    slash,
                    section,
                    grayscale=True,
                    return_confidence=True
                )
                if c < 0.9: continue
                
                text = fix_digits(''.join(OCR_Handler.get_text(section)).replace(' ', '').replace('/', ''))
                available = int(text[0])
                return available
            except (KeyboardInterrupt, SystemExit): raise
            except Exception as e:
                logger.error(f"Upgrader.get_builder_builders: {e}")
            time.sleep(0.5)
        logger.error("Upgrader.get_builder_builders: Failed to get builder builders")
        raise Exception("Failed to get builder builders")

    def home_lab_available(self, timeout=60, use_cached_frame=False):
        import time
        
        start = time.time()
        while time.time() < start + timeout:
            try:
                section = Frame_Handler.get_frame_section(0.94, 0.75, -0.02, -0.21, high_contrast=True, use_cached=use_cached_frame)
                if configs.DEBUG: Frame_Handler.save_frame(section, "home_lab.png")
                
                # Find the backslash
                slash = render_text("/", "SupercellMagic", 24)
                x, y, c = Frame_Handler.locate(
                    slash,
                    section,
                    grayscale=True,
                    return_confidence=True
                )
                if c < 0.9: continue
                
                # Extract text
                text = fix_digits(''.join(OCR_Handler.get_text(section)).replace(' ', '').replace('/', ''))
                available = int(text[0])
                return available > 0
            except (KeyboardInterrupt, SystemExit): raise
            except Exception as e:
                logger.error(f"Upgrader.home_lab_available: {e}")
            time.sleep(0.5)
        logger.error("Upgrader.home_lab_available: Failed to get home lab availability")
        raise Exception("Failed to get home lab availability")

    def builder_lab_available(self, timeout=60, use_cached_frame=False):
        import time
        
        start = time.time()
        while time.time() < start + timeout:
            try:
                section = Frame_Handler.get_frame_section(0.94, 0.75, -0.02, -0.21, high_contrast=True, use_cached=use_cached_frame)
                if configs.DEBUG: Frame_Handler.save_frame(section, "builder_lab.png")
                
                # Find the backslash
                slash = render_text("/", "SupercellMagic", 24)
                x, y, c = Frame_Handler.locate(
                    slash,
                    section,
                    grayscale=True,
                    return_confidence=True
                )
                if c < 0.9: continue
                
                # Extract text
                text = fix_digits(''.join(OCR_Handler.get_text(section)).replace(' ', '').replace('/', ''))
                available = int(text[0])
                return available > 0
            except (KeyboardInterrupt, SystemExit): raise
            except Exception as e:
                logger.error(f"Upgrader.builder_lab_available: {e}")
            time.sleep(0.5)
        logger.error("Upgrader.builder_lab_available: Failed to get builder lab availability")
        raise Exception("Failed to get builder lab availability")
    
    @require_exit(x=0.99, y=0.01)
    def pet_house_available(self, timeout=60, use_cached_frame=False):
            import time
            
            self._click_build_button()
            start = time.time()
            while time.time() < start + timeout:
                try:
                    section = Frame_Handler.get_frame_section(0.95, 0.94, -0.02, -0.02, high_contrast=True, use_cached=use_cached_frame)
                    if configs.DEBUG: Frame_Handler.save_frame(section, "pet_house.png")
                    
                    # Find the backslash
                    slash = render_text("/", "SupercellMagic", 16)
                    x, y, c = Frame_Handler.locate(
                        slash,
                        section,
                        grayscale=True,
                        return_confidence=True
                    )
                    if c < 0.9: continue
                    
                    # Extract text
                    text = fix_digits(''.join(OCR_Handler.get_text(section)).replace(' ', '').replace('/', ''))
                    available = int(text[0])
                    return available > 0
                except (KeyboardInterrupt, SystemExit): raise
                except Exception as e:
                    logger.error(f"Upgrader.pet_house_available: {e}")
                time.sleep(0.5)
            logger.error("Upgrader.pet_house_available: Failed to get pet house availability")
            raise Exception("Failed to get pet house availability")

    def collect_builder_attack_elixir(self):
        import time
        
        # Align view to top right corner
        Input_Handler.zoom(dir="out")
        for _ in range(3):
            Input_Handler.swipe_down(duration=0)
        for _ in range(3):
            Input_Handler.swipe_left(duration=0)
        Input_Handler.swipe_left(duration=0, hold_end_time=500)
        time.sleep(0.5)
        
        # Open elixir cart menu
        Input_Handler.click(0.61, 0.47)
        time.sleep(0.5)
        
        # Collect elixir
        x, y = Frame_Handler.locate(self.assets["collect"], grayscale=False, thresh=0.9)
        if x is not None and y is not None:
            Input_Handler.click(x, y)
            time.sleep(0.1)
        Input_Handler.click_exit(n=5, delay=0.1)
        time.sleep(1) # let the cart window close before the builder count is read

    # ============================================================
    # 🧱 Upgrade Management
    # ============================================================

    def _get_suggested_upgrade_template(self):
        template = render_text("Suggested upgrades", "SupercellMagic", 15, color=(195, 172, 166))
        return template
    
    def _get_pet_assigned_templates(self):
        assigned_template = render_text("Assigned", "SupercellMagic", 15, color=(195, 172, 166))
        unassigned_template = render_text("Unassigned", "SupercellMagic", 15, color=(195, 172, 166))
        return assigned_template, unassigned_template
    
    def _get_assistant_available_template(self):
        return render_text("Available", "CCBackBeat", 25)
    
    def _get_upgrade_templates(self, upgrade_text, include_new=True, font_size=17):
        templates = [render_text(text, "SupercellMagic", font_size) for text in upgrade_text]
        if include_new:
            templates += [render_text(text, "SupercellMagic", font_size, color=(180, 247, 86)) for text in upgrade_text]
        return templates
    
    def _get_sufficient_resources(self, section):
        return not check_color((255, 123, 114), section, tol=10)

    def _get_upgrade_name(self, categories=["all"]):
        import numpy as np
        x, y = Frame_Handler.locate(self.assets["upgrade_name"], ref="lc", thresh=0.9)
        assert x is not None and y is not None, "Failed to locate upgrade name"
        section = Frame_Handler.get_frame_section(x+0.122, y-0.04, 1-x, y+0.035, high_contrast=True, thresh=255, use_cached=True)
        if configs.DEBUG: Frame_Handler.save_frame(section, "upgrade_name.png")
        upgrade_names = get_vocab_in_categories(categories)
        templates = self._get_upgrade_templates(upgrade_names, include_new=False, font_size=35)
        # upgrade_name = spell_check(re.sub(r"\s*x\d+$", "", OCR_Handler.get_text(section)[0].lower()[:-3]), categories, phrase_level=True)
        res = Frame_Handler.batch_locate(templates, section, thresh=0.0, grayscale=True, return_confidence=True)
        return upgrade_names[np.argmax([c for x, y, c in res])].lower()

    def _get_upgrade_menu(self, frame, return_bounds=False, pet_house=False):
        menu_left = 0.775 if not pet_house else 0.8
        menu_top = 0.06
        menu_right = 1.0
        menu_bottom = 0.9
        menu = Frame_Handler.crop(frame, menu_left, menu_top, menu_right, menu_bottom)
        if return_bounds: return menu, menu_left, menu_top, menu_right, menu_bottom
        return menu

    def _get_potential_upgrade_locs(self, menu, exclude_new=False):
        import numpy as np
        from scipy.ndimage import gaussian_filter1d
        
        def profile_bounds(profile):
            bounds = []
            prev_val = 0
            for i, val in enumerate(profile):
                if prev_val == 0 and val == 1:
                    bounds.append(i)
                if prev_val == 1 and val == 0:
                    bounds.append(i)
                prev_val = val
            if prev_val == 1:
                bounds.append(len(profile))
            bounds = np.array(bounds).reshape((-1, 2))
            centers = (bounds[:, 0] + bounds[:, 1]) / 2
            return bounds, centers
        
        menu_white = filter_color([255, 255, 255], menu, tol=0, return_mask=True)[1]
        menu_green = filter_color([180, 247, 86], menu, tol=0, return_mask=True)[1]
        # menu_red = filter_color((255, 123, 114), menu, tol=0, return_mask=True)[1]
        white_profile = np.where(gaussian_filter1d(menu_white.mean(axis=1), sigma=1) > 0.01, 1, 0)
        green_profile = np.where(gaussian_filter1d(menu_green.mean(axis=1), sigma=1) > 0.01, 1, 0)
        # red_profile = np.where(gaussian_filter1d(menu_red.mean(axis=1), sigma=1) > 0.01, 1, 0)
        white_bounds, white_centers = profile_bounds(white_profile)
        green_bounds, green_centers = profile_bounds(green_profile)
        # red_bounds, red_centers = profile_bounds(red_profile)
        potential_y_locs = [] # in pixels
        
        for i in range(len(white_centers)-1):
            wc = white_centers[i]
            wc_next = white_centers[i+1]
            if (abs(wc_next - wc) < 50) and (not exclude_new or all(abs(green_centers - wc) > 50)):
                potential_y_locs.append(wc)
        return np.array(potential_y_locs)

    def _find_builder_confirm(self):
        import cv2, numpy as np
        from scipy.ndimage import gaussian_filter1d
        thresh = 0.2
        section = Frame_Handler.get_frame_section(0.0, 0.9, 1.0, 0.92, grayscale=False)
        section = cv2.cvtColor(section, cv2.COLOR_RGB2LAB).astype(np.float32)
        btn_color = cv2.cvtColor(np.array([[[189, 230, 76]]], dtype=np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
        diff = np.linalg.norm((section - btn_color)/255, axis=2).mean(0)
        diff = gaussian_filter1d(diff, sigma=10)
        min_loc = np.argmin(diff)
        x = min_loc / section.shape[1]
        if diff[min_loc] > thresh: return None, None
        x1 = x
        i = min_loc
        while i > 0 and diff[i] < thresh:
            x1 = i / section.shape[1]
            i -= 1
        x2 = x
        i = min_loc
        while i < section.shape[1]-1 and diff[i] < thresh:
            x2 = i / section.shape[1]
            i += 1
        x = (x1 + x2) / 2
        y = 0.85
        return x, y
    
    def _scroll_locate_upgrade(self, locate_func, menu_left, menu_right, menu_top, menu_bottom, dir="down"):
        # First two return values of locate_func should be x and y of located upgrade
        import time, numpy as np
        menu_center = (menu_left + menu_right) / 2
        res = locate_func()
        if res[0] is None or res[1] is None:
            prev_section = Frame_Handler.get_frame_section(menu_left, menu_top, menu_right, menu_bottom, high_contrast=True, thresh=255)
            for _ in range(20):
                if dir == "down":
                    y1, y2 = menu_bottom-0.075, menu_top
                elif dir == "up":
                    y1, y2 = menu_top+0.075, menu_bottom
                Input_Handler.swipe(x1=menu_center, y1=y1, x2=menu_center, y2=y2, duration=0, hold_end_time=100)
                time.sleep(0.1)
                
                # Check if at end of upgrade menu
                section = Frame_Handler.get_frame_section(menu_left, menu_top, menu_right, menu_bottom, high_contrast=True, thresh=255)
                diff = np.abs(section - prev_section).mean() / 255
                if diff < 0.01: break
                prev_section = section
                
                res = locate_func()
                if res[0] is not None and res[1] is not None: break
        return res
    
    # ============================================================
    # 💲 Menu Scan (costs, cheapest, minimums, discounts)
    # ============================================================

    # Measured at 1920x1080: a menu row is "name ... time" over "... cost (resource icon)"
    COST_ICON_X = (0.981, 0.991)
    COST_TEXT_X = (0.840, 0.979)
    NAME_DY = 0.025 # the name line sits this far above the cost line
    MAX_MENU_PAGES = 25
    MENUS = {
        "home": {"categories": ["buildings/home-village", "traps/home-village", "heroes", "guardians"], "name_x_max": 0.79},
        "lab": {"categories": ["troops", "spells"], "name_x_max": 0.79},
        "pet": {"categories": ["pets"], "name_x_max": 0.82}, # assigned pets have two portraits, name starts further right
    }

    def _menu_header_y(self, kind, frame):
        """y of the label above the upgrade rows ("Suggested upgrades", or "Assigned"/"Unassigned" for pets)."""
        if kind == "pet":
            ys = [y for x, y in Frame_Handler.batch_locate(list(self._get_pet_assigned_templates()), frame, thresh=0.70, grayscale=True, prefilter=True) if y is not None]
            return min(ys) if ys else None
        return Frame_Handler.locate(self._get_suggested_upgrade_template(), frame, thresh=0.70, grayscale=True, prefilter=True)[1]

    def _open_menu(self, kind):
        """Open an upgrade list and scroll its header to the top (ongoing upgrades out of view). Returns the menu bounds."""
        import time
        self._click_build_button()
        time.sleep(0.5)
        {"home": self._click_home_builders, "lab": self._click_home_lab, "pet": self._click_pet_house}[kind]()
        time.sleep(0.5)
        frame = Frame_Handler.get_frame(grayscale=False)
        Frame_Handler.save_frame(frame, f"menu_{kind}.png") # the ongoing upgrades and their times (builder status, Emre 02.11)
        _, left, top, right, bottom = self._get_upgrade_menu(frame, return_bounds=True, pet_house=kind == "pet")
        y_header = self._menu_header_y(kind, frame)
        if y_header is None: return None
        Input_Handler.swipe_up(x=(left + right) / 2, y1=y_header, y2=top, duration=0, hold_end_time=100)
        time.sleep(0.3)
        return left, top, right, bottom

    def _menu_swipe(self, bounds):
        import time
        left, top, right, bottom = bounds
        # Pages overlap by about two rows, so a row cut by the edge of one page is whole on the next
        Input_Handler.swipe(x1=(left + right) / 2, y1=bottom - 0.075, x2=(left + right) / 2, y2=top + 0.15, duration=0, hold_end_time=100)
        time.sleep(0.3)

    def _cost_icons(self, frame, y1, y2):
        """(y, resource) of every gold / elixir / dark elixir icon in the cost column between y1 and y2."""
        h = frame.shape[0]
        top = int(h * y1)
        col = Frame_Handler.crop(frame, self.COST_ICON_X[0], y1, self.COST_ICON_X[1], y2).astype(int)
        r, g, b = col[..., 0], col[..., 1], col[..., 2]
        masks = {
            "gold": (r > 200) & (g > 150) & (b < 90),
            "elixir": (r > 140) & (g < 110) & (b > 150),
            "dark": (r < 70) & (g < 55) & (b < 75),
        }
        icons = []
        for resource, mask in masks.items():
            # Row separators are 1-2 px dark lines and the clock icon has a few yellow pixels, an icon is a solid run
            on = list(mask.mean(axis=1) > 0.3) + [False]
            start = None
            for i, v in enumerate(on):
                if v and start is None: start = i
                elif not v and start is not None:
                    if i - start >= 6: icons.append(((top + (start + i) / 2) / h, resource))
                    start = None
        # The shine on the dark elixir drop can split one icon into two runs
        merged = []
        for y, resource in sorted(icons):
            if merged and merged[-1][1] == resource and y - merged[-1][0] < 0.02:
                merged[-1] = ((merged[-1][0] + y) / 2, resource)
            else: merged.append((y, resource))
        return merged

    def _read_cost(self, frame, y):
        """Cost left of the resource icon at y: (amount or None, affordable). Red digits = not enough resources."""
        import numpy as np
        section = Frame_Handler.crop(frame, self.COST_TEXT_X[0], y - 0.016, self.COST_TEXT_X[1], y + 0.016)
        s = section.astype(int)
        white = s.min(axis=2) > 200
        red = (s[..., 0] > 200) & (s[..., 1] > 80) & (s[..., 1] < 170) & (s[..., 2] > 70) & (s[..., 2] < 160)
        affordable = white.sum() > red.sum()
        if not affordable: return None, False
        digits = "".join(ch for ch in OCR_Handler.read_mask(white) if ch.isdigit())
        return (int(digits) if digits else None), True

    def _row_is_new(self, frame, left, y):
        # Buildings not built yet have a green name and a green "New" label
        band = Frame_Handler.crop(frame, left, y - self.NAME_DY - 0.015, self.COST_TEXT_X[0], y + 0.015)
        return filter_color([180, 247, 86], band, tol=10, return_mask=True)[1].mean() > 0.003

    def _row_is_discounted(self, frame, left, y):
        # Discounts (Hammer Jam etc.) put a small lime-green tag on the row's top-left corner, left of the menu bounds.
        # Measured 01.11: ~235 tag pixels on a discounted row, 0 on the others; the old template was larger than the tag
        corner = Frame_Handler.crop(frame, 0.732, y - 0.057, 0.755, y - 0.020).astype(int)
        r, g, b = corner[..., 0], corner[..., 1], corner[..., 2]
        return ((g > 170) & (r > 60) & (r < 200) & (b < 70) & (g - r > 40)).mean() > 0.04

    def _read_rows(self, frame, kind, bounds, y_min, names=[], templates=[]):
        """Every fully visible row on screen: cost, resource, affordable, new, discounted and which of names it shows."""
        left, top, right, bottom = bounds
        menu = Frame_Handler.crop(frame, left, top, right, bottom)
        mh, mw = menu.shape[:2]
        h, w = frame.shape[:2]
        matches = Frame_Handler.batch_locate(templates, menu, thresh=0.70, ref="lc", grayscale=False, prefilter=True, return_all=True) if templates else []
        name_x_max = self.MENUS[kind]["name_x_max"]
        rows = []
        for y, resource in self._cost_icons(frame, y_min, bottom):
            name_y = y - self.NAME_DY
            if name_y - 0.015 < y_min or y + 0.02 > bottom: continue
            cost, affordable = self._read_cost(frame, y)
            row = {
                "y": y, "name_y": name_y, "resource": resource, "cost": cost, "affordable": affordable,
                "new": self._row_is_new(frame, left, y), "discount": self._row_is_discounted(frame, left, y), "names": set(),
            }
            for name, found in zip(names, matches):
                for x, ym in found:
                    if x is None: continue
                    # Only a match at the start of the name counts ("Barracks" inside "Dark Barracks" does not)
                    if left + x * mw / w < name_x_max and abs(top + ym * mh / h - name_y) < 0.012:
                        row["names"].add(name.lower())
                        break
            rows.append(row)
        return rows

    def _scan_menu(self, kind, bounds, names):
        """Scroll the open menu from top to bottom and read every row. Returns (rows, index of the page on screen)."""
        import numpy as np
        left, top, right, bottom = bounds
        templates = [render_text(name, "SupercellMagic", 17) for name in names]
        frame = Frame_Handler.get_frame(grayscale=False)
        rows, page = [], 0
        while True:
            y_min = top
            if page == 0: y_min = max(top, self._menu_header_y(kind, frame) or top)
            rows += [dict(row, page=page) for row in self._read_rows(frame, kind, bounds, y_min, names, templates)]
            if page + 1 >= self.MAX_MENU_PAGES: break
            self._menu_swipe(bounds)
            new_frame = Frame_Handler.get_frame(grayscale=False)
            a = Frame_Handler.grayscale(Frame_Handler.crop(frame, left, top, right, bottom)).astype(int)
            b = Frame_Handler.grayscale(Frame_Handler.crop(new_frame, left, top, right, bottom)).astype(int)
            if np.abs(a - b).mean() / 255 < 0.01: break # end of the list
            frame, page = new_frame, page + 1
        return rows, page

    def _goto_row(self, kind, bounds, row, page):
        """Tap the chosen row. If it scrolled away, reopen the menu, replay the swipes and find it again by cost."""
        import time
        left, top, right, bottom = bounds
        y = row["name_y"]
        if row["page"] != page:
            Input_Handler.click_exit(x=0.99, y=0.01, n=3, delay=0.1)
            time.sleep(0.5)
            bounds = self._open_menu(kind)
            if bounds is None: return False
            for _ in range(row["page"]): self._menu_swipe(bounds)
            frame = Frame_Handler.get_frame(grayscale=False)
            same = [r for r in self._read_rows(frame, kind, bounds, top) if r["cost"] == row["cost"] and r["resource"] == row["resource"]]
            if not same:
                logger.warning(f"Chosen upgrade not found again ({row['resource']} {row['cost']})")
                return False
            y = min(same, key=lambda r: abs(r["y"] - row["y"]))["name_y"]
        Input_Handler.click((left + right) / 2, y)
        time.sleep(0.5)
        return True

    def _cost_key(self, row):
        """Sort key for "cheapest": preferred resource first, then cost as a share of what is in storage."""
        prefer = Settings_Handler.get("home", "prefer_resource", "any")
        have = Resource_Reader.last.get(row["resource"])
        share = row["cost"] / have if have else float("inf")
        return (0 if prefer in ("any", row["resource"]) else 1, share)

    def _keeps_minimum(self, row):
        keep = Settings_Handler.get("home", f"keep_{row['resource']}", 0) or 0
        have = Resource_Reader.last.get(row["resource"])
        if keep <= 0: return True
        return have is not None and have - row["cost"] >= keep

    def _home_blocked_names(self):
        """Home base upgrades the panel forbids right now, as {lowercase name: in-game name}. Walls have their own pass."""
        blocked = {name.lower(): name for name in Settings_Handler.get("home", "excluded", [])}
        blocked["crafting station"] = "Crafting Station"
        blocked["wall"] = "Wall"
        if Task_Handler.excluded("heroes"):
            for hero in (Cache_Manager.get("vocab") or get_vocab())["heroes"]: blocked[hero.lower()] = hero
        return blocked

    def _hero_names(self):
        return {hero.lower() for hero in (Cache_Manager.get("vocab") or get_vocab())["heroes"]}

    def _choose_row(self, rows, priority, blocked, first=(), only=None):
        """Discounted first, then the priority list, then cheapest (or random); Town Hall only when nothing else fits.
        first: levels tried before everything, even discounts (the heroes, when the panel puts them first).
        only: lowercase names, nothing else may be chosen (the builders kept for heroes)."""
        import random
        eligible = [
            r for r in rows
            if r["affordable"] and not r["new"] and r["cost"] is not None
            and not (r["names"] & blocked) and self._keeps_minimum(r)
            and (only is None or r["names"] & only)
        ]
        for level in first:
            level = {name.lower() for name in level}
            candidates = [r for r in eligible if r["names"] & level]
            if candidates: return min(candidates, key=self._cost_key), "heroes first"
        town_hall = [r for r in eligible if "town hall" in r["names"]]
        others = [r for r in eligible if "town hall" not in r["names"]]
        if Settings_Handler.get("home", "discount_first", True):
            discounted = [r for r in others if r["discount"]]
            if discounted: return min(discounted, key=self._cost_key), "discount"
        for level in priority:
            level = {name.lower() for name in level}
            candidates = [r for r in eligible if r["names"] & level]
            if candidates: return min(candidates, key=self._cost_key), "priority"
        if others:
            if Settings_Handler.get("home", "fallback", "cheapest") == "random": return random.choice(others), "random"
            return min(others, key=self._cost_key), "cheapest"
        if town_hall: return town_hall[0], "town hall"
        return None, None

    @require_exit(x=0.99, y=0.01)
    def _menu_upgrade(self, kind, priority, first=(), only=None):
        """Start one upgrade from the home builders (kind "home"), laboratory ("lab") or pet house ("pet") menu."""
        import time

        try:
            blocked = {}
            if kind == "home":
                blocked = self._home_blocked_names()
                if not Settings_Handler.get("home", "town_hall", True): blocked["town hall"] = "Town Hall"
            names = sorted({name for level in list(first) + list(priority) for name in level} | set(blocked.values()) | ({"Town Hall"} if kind == "home" else set()))

            start = time.time()
            bounds = self._open_menu(kind)
            if bounds is None: return None
            rows, page = self._scan_menu(kind, bounds, names)
            row, reason = self._choose_row(rows, priority, set(blocked), first=first, only=only)
            affordable = [r for r in rows if r["affordable"]]
            unread = sum(1 for r in affordable if r["cost"] is None)
            logger.info(f"Menu {kind}: {len(rows)} rows, {len(affordable)} affordable, {unread} unread, {int(time.time() - start)}s")
            if row is None:
                logger.info(f"No upgrade fits ({kind})")
                return None
            cost = f"{row['cost']:,}".replace(",", ".")
            logger.info(f"Chosen ({reason}): {row['resource']} {cost}{' discounted' if row['discount'] else ''}")
            self.last_choice = (row["resource"], row["cost"])
            if not self._goto_row(kind, bounds, row, page): return None

            if kind == "home":
                upgrade_name = self._get_upgrade_name(self.MENUS["home"]["categories"])
                if upgrade_name in blocked:
                    logger.info(f"Skipped {upgrade_name}: blocked in the panel")
                    return None
            else:
                upgrade_name = self._get_upgrade_name(self.MENUS[kind]["categories"])

            if self.dry_run:
                logger.info(f"Dry run, not confirming: {upgrade_name}")
                return None
            if not self._click_home_confirm(): return None
            time.sleep(0.5)
            return upgrade_name
        except (KeyboardInterrupt, SystemExit): raise
        except Exception:
            logger.exception(f"Upgrader._menu_upgrade({kind}):")
            return None

    @require_exit(x=0.99, y=0.01)
    def home_upgrade(self, heroes_only=False):
        """heroes_only: the free builders left are kept for heroes, or Buildings is off and only Heroes is on.
        The heroes' own order (panel Geliştirme → Kahramanlar) goes before everything when "heroes first" is on,
        otherwise after the buildings' order (and they still take part in "cheapest")."""
        priority = [] if Task_Handler.excluded("home_base_priority") else configs.HOME_BASE_UPGRADE_PRIORITY
        heroes = [] if Task_Handler.excluded("heroes") else [level for level in Settings_Handler.get("home", "hero_priority", []) if level]
        first = heroes if heroes_only or Settings_Handler.get("home", "heroes_first", False) else []
        later = ([] if heroes_only else priority) + ([] if first else heroes)
        return self._menu_upgrade("home", later, first=first, only=self._hero_names() if heroes_only else None)

    # ============================================================
    # 🧱 Walls (no builder needed, upgrade instantly)
    # ============================================================

    def _wall_payment(self, cost):
        """Gold first down to its panel minimum, then elixir down to its minimum (Emre 01.11): run_walls pays one batch per resource."""
        last = Resource_Reader.last
        for resource, key in (("gold", "min_gold"), ("elixir", "min_elixir")):
            have = last.get(resource)
            if have is not None and have - cost >= Settings_Handler.get("walls", key, 0): return resource
        return None

    def _click_wall_button(self, resource):
        """Tap the gold or elixir Upgrade button under a selected wall, found by the icon next to its price."""
        h, w = WINDOW_DIMS[1], WINDOW_DIMS[0]
        x1, y1, x2, y2 = 0.15, 0.80, 0.60, 0.845
        band = Frame_Handler.get_frame_section(x1, y1, x2, y2, grayscale=False).astype(int)
        r, g, b = band[..., 0], band[..., 1], band[..., 2]
        mask = (r > 200) & (g > 150) & (b < 90) if resource == "gold" else (r > 140) & (g < 110) & (b > 150)
        cols = list(mask.sum(axis=0) > 3) + [False]
        # Largest run of icon columns; coins in the village can peek out next to the buttons
        best, start = None, None
        for i, v in enumerate(cols):
            if v and start is None: start = i
            elif not v and start is not None:
                if best is None or i - start > best[1] - best[0]: best = (start, i)
                start = None
        if best is None or best[1] - best[0] < 8: return False
        icon_x = x1 + (best[0] + best[1]) / 2 / w
        Input_Handler.click(icon_x - 0.035, 0.88)
        return True

    @staticmethod
    def _selected_wall_level():
        """Level in the "Wall (Level 12)" title over the selected wall, or None. The ")" is sometimes read as a 1 ("Level 131")."""
        import re
        frame = Frame_Handler.get_frame(grayscale=False)
        for text in OCR_Handler.get_text(Frame_Handler.crop(frame, 0.15, 0.45, 0.80, 0.72)):
            text = text.lower().replace("i", "1").replace("|", "1").replace("o", "0")
            m = re.search(r"wa(?:ll|11).*leve[l1]\s*(\d+)", text)
            if not m: continue
            digits = m.group(1)[:2]
            if int(digits) > 18: digits = digits[:1]
            return int(digits)
        return None

    def _menu_swipe_back(self, bounds):
        import time
        left, top, right, bottom = bounds
        # The reverse of _menu_swipe: one page back up
        Input_Handler.swipe(x1=(left + right) / 2, y1=top + 0.15, x2=(left + right) / 2, y2=bottom - 0.075, duration=0, hold_end_time=100)
        time.sleep(0.3)

    def _select_wall(self, bounds):
        """Read every wall row in the open menu (they sit together), then tap the cheapest one = the lowest level that is
        affordable, payable and of a chosen level, scrolling back to its page. Returns the row, or None."""
        import time, numpy as np
        left, top, right, bottom = bounds
        levels = set(Settings_Handler.get("walls", "levels", []) or [])
        known = getattr(self, "_wall_levels", {}) # cost -> level, remembered between walls
        self._wall_levels = known
        templates = [render_text("Wall", "SupercellMagic", 17)]
        read = lambda frame, y_min: [r for r in self._read_rows(frame, "home", bounds, y_min, ["Wall"], templates) if "wall" in r["names"] and r["cost"]]

        # 1) Scroll down until the wall rows are behind us; a higher level can come before a lower one in the list
        frame = Frame_Handler.get_frame(grayscale=False)
        rows, page = {}, 0 # cost -> row (pages overlap, so the same row can be read twice)
        while True:
            y_min = max(top, self._menu_header_y("home", frame) or top) if page == 0 else top
            walls = read(frame, y_min)
            for r in walls: rows.setdefault(r["cost"], dict(r, page=page))
            if rows and not walls: break
            if page + 1 >= self.MAX_MENU_PAGES: break
            self._menu_swipe(bounds)
            new_frame = Frame_Handler.get_frame(grayscale=False)
            a = Frame_Handler.grayscale(Frame_Handler.crop(frame, left, top, right, bottom)).astype(int)
            b = Frame_Handler.grayscale(Frame_Handler.crop(new_frame, left, top, right, bottom)).astype(int)
            if np.abs(a - b).mean() / 255 < 0.01: break # end of the list
            frame, page = new_frame, page + 1

        # 2) Cheapest first: scroll to its page, find it again by cost, tap it, check its level when levels are chosen
        for r in sorted(rows.values(), key=lambda r: r["cost"]):
            if not r["affordable"] or self._wall_payment(r["cost"]) is None: continue
            if levels and known.get(r["cost"]) is not None and known[r["cost"]] not in levels: continue
            while page > r["page"]:
                self._menu_swipe_back(bounds); page -= 1
            while page < r["page"]:
                self._menu_swipe(bounds); page += 1
            same = []
            for _ in range(2): # page boundaries drift a little: one more step back if the row is not on screen
                same = [x for x in read(Frame_Handler.get_frame(grayscale=False), top) if x["cost"] == r["cost"]]
                if same: break
                self._menu_swipe_back(bounds); page -= 1
            if not same:
                logger.info(f"Wall row not found again ({r['cost']:,})".replace(",", "."))
                continue
            Input_Handler.click((left + right) / 2, same[0]["name_y"])
            if levels and known.get(r["cost"]) in levels: time.sleep(0.7) # level already confirmed for this cost
            elif levels:
                # OCR once read 12 as 11 and the walls were skipped for the rest of the session:
                # a level counts only when two reads agree, and only an agreed level is remembered
                reads = []
                for _ in range(5): # the view slides to the wall first
                    time.sleep(0.6)
                    value = self._selected_wall_level()
                    if value is not None: reads.append(value)
                    if len(reads) >= 2 and reads[-1] == reads[-2]: break
                agreed = len(reads) >= 2 and reads[-1] == reads[-2]
                level = reads[-1] if agreed else None
                if agreed: known[r["cost"]] = level
                if level not in levels:
                    logger.info(f"Wall level {level if level is not None else '?'} not chosen ({r['cost']:,})".replace(",", "."))
                    continue
            else: time.sleep(0.7)
            return same[0]

        if not rows: logger.info("No wall in the menu")
        elif levels: logger.info(f"No wall of the chosen levels ({', '.join(map(str, sorted(levels)))})")
        else:
            last = Resource_Reader.last
            fmt = lambda v: "-" if v is None else f"{v:,}".replace(",", ".")
            logger.info(f"Walls skipped: gold {fmt(last.get('gold'))} min {fmt(Settings_Handler.get('walls', 'min_gold', 0))}, elixir {fmt(last.get('elixir'))} min {fmt(Settings_Handler.get('walls', 'min_elixir', 0))}")
        return None

    @staticmethod
    def _selected_wall_count():
        """N in the "Wall (Level 12) x N" title once Upgrade More is on, or None."""
        import re
        frame = Frame_Handler.get_frame(grayscale=False)
        for text in OCR_Handler.get_text(Frame_Handler.crop(frame, 0.15, 0.45, 0.80, 0.72)):
            m = re.search(r"x\s*([\dil|otsz]+)\s*$", text.lower()) # OCR reads 1 as I / l / T
            if "lev" in text.lower() and m: return int(m.group(1).translate(str.maketrans("il|otsz", "1110152")))
        return None

    def _add_walls(self, n):
        """Turn on Upgrade More under the selected wall and add walls until n are selected. Returns how many are selected.
        +1 takes the place of Upgrade More, +10 is one button to its left, -1 two buttons to its left."""
        import time, cv2
        if n <= 1: return 1
        if not hasattr(self, "_more_tpl"):
            self._more_tpl = cv2.cvtColor(cv2.imread(str(Asset_Manager.resource_path("assets/upgrader/upgrade_more.png"))), cv2.COLOR_BGR2RGB)
        x, y = Frame_Handler.locate(self._more_tpl, grayscale=False, thresh=0.85)
        if x is None: return 1
        Input_Handler.click(x, y)
        time.sleep(0.6)
        for _ in range((n - 1) // 10):
            Input_Handler.click(x - 0.108, y)
            time.sleep(0.35)
        for _ in range((n - 1) % 10):
            Input_Handler.click(x, y)
            time.sleep(0.3)
        count = None
        for _ in range(3): # OCR misses the title now and then
            time.sleep(0.4)
            count = self._selected_wall_count()
            if count is not None: break
        for _ in range(12): # never pay for more than was asked
            if count is None or count <= n: break
            Input_Handler.click(x - 0.216, y)
            time.sleep(0.4)
            count = self._selected_wall_count()
        return count

    @staticmethod
    def _wall_debug(message):
        # Silent failures used to end the wall pass without a trace: say why and keep the screen
        logger.warning(message)
        Frame_Handler.save_frame(Frame_Handler.get_frame(grayscale=False), "wall_fail.png")

    @require_exit(x=0.99, y=0.01)
    def wall_upgrade(self, max_walls=1):
        """Upgrade up to max_walls walls of one level in one go (Upgrade More), keeping the panel minimums.
        Returns (resource paid, number of walls), or None."""
        import time

        try:
            bounds = self._open_menu("home")
            if bounds is None:
                self._wall_debug("Walls: the upgrade menu did not open")
                return None
            row = self._select_wall(bounds)
            if row is None: return None
            resource = self._wall_payment(row["cost"])
            have = Resource_Reader.last.get(resource) or 0
            keep = Settings_Handler.get("walls", "min_gold" if resource == "gold" else "min_elixir", 0) or 0
            n = max(1, min(max_walls, (have - keep) // row["cost"]))
            count = self._add_walls(n)
            if count is None or count < 1 or count * row["cost"] > have - keep:
                self._wall_debug(f"Walls: selected wall count unclear ({count}, wanted {n})")
                return None
            if not self._click_wall_button(resource):
                logger.warning(f"Wall {resource} button not found")
                return None
            time.sleep(0.5)
            if self.dry_run:
                cost = f"{row['cost']:,}".replace(",", ".")
                logger.info(f"Dry run, not confirming: {count} wall(s) with {resource}, {cost} each")
                return None
            if not (self._click_walls_confirm() if count > 1 else self._click_home_confirm()):
                self._wall_debug("Walls: confirm button not found")
                return None
            time.sleep(0.5)
            return resource, count
        except (KeyboardInterrupt, SystemExit): raise
        except Exception:
            logger.exception("Upgrader.wall_upgrade:")
            return None

    def run_walls(self):
        import time
        if not Settings_Handler.get("walls", "enabled", False):
            logger.info("Walls skipped: disabled")
            return
        left = Settings_Handler.get("walls", "max_per_round", 5)
        # Cheapest wall seen so far: when neither resource can pay it, skip the menu (it takes ~30 s to look through)
        known = [c for c in getattr(self, "_wall_levels", {})]
        if known and self._wall_payment(min(known)) is None:
            logger.info("Walls skipped: not enough gold or elixir for a wall")
            return
        while left > 0:
            before = Resource_Reader.last
            result = self.wall_upgrade(left)
            if result is None: break
            resource, count = result
            time.sleep(0.5)
            after = Resource_Reader.read() or {}
            # Walls finish instantly, so they count only if the resource actually went down
            if (after.get(resource) or 0) >= (before.get(resource) or 0):
                logger.warning(f"Walls: paid with {resource} but it did not go down ({before.get(resource)} -> {after.get(resource)})")
                break
            logger.info(f"Upgraded {count} wall(s)")
            report("wall", count=count)
            left -= count

    @require_exit(x=0.99, y=0.01)
    def assign_builder_apprentice(self):
        """True = assigned, False = nothing to assign (none free, or no upgrade running), None = error."""
        import time
        
        try:
            # Open upgrade list menu
            self._click_build_button()
            time.sleep(0.5)
            Frame_Handler.save_frame(Frame_Handler.get_frame(grayscale=False), "menu_build_bar.png") # builders / lab / pet counts
            self._click_home_builders()
            time.sleep(1.0)
            # The builders menu as it opens: the ongoing upgrades with their times are on top (builder status, Emre 02.11)
            Frame_Handler.save_frame(Frame_Handler.get_frame(grayscale=False), "menu_builders_top.png")

            # Find assistant available label
            xys = Frame_Handler.locate(self._get_assistant_available_template(), thresh=0.8, return_all=True)
            xys = sorted(xys, key=lambda pair: pair[1])
            if len(xys) == 0: return False
            x, y = xys[0]
            if x is None or y is None: return False

            Input_Handler.click(x, y)
            time.sleep(0.5)
            
            # Find assign assistant label
            xys = Frame_Handler.locate(self.assets["assign_assistant"], thresh=0.9, grayscale=False, return_all=True)
            if len(xys) == 0: return False
            
            x, y = sorted(xys, key=lambda pair: pair[1])[0]
            if x is None or y is None: return False
            
            Input_Handler.click(x, y)
            time.sleep(0.5)
            
            # Find confirm button
            x, y = Frame_Handler.locate(self.assets["confirm_assistant"], grayscale=False, thresh=0.9)
            if x is None or y is None: return False
            
            Input_Handler.click(x, y)
            time.sleep(0.5)
            return True
        except (KeyboardInterrupt, SystemExit): raise
        except Exception:
            logger.exception("Upgrader.assign_builder_apprentice:")
    
    @require_exit(x=0.99, y=0.01)
    def home_lab_upgrade(self):
        priority = [] if Task_Handler.excluded("home_lab_priority") else configs.HOME_LAB_UPGRADE_PRIORITY
        return self._menu_upgrade("lab", priority)

    @require_exit(x=0.99, y=0.01)
    def assign_lab_assistant(self):
        """True = assigned, False = nothing to assign (none free, or no upgrade running), None = error."""
        import time
        
        try:
            # Open upgrade list menu
            self._click_build_button()
            time.sleep(0.5)
            self._click_home_lab()
            time.sleep(1.0)
            Frame_Handler.save_frame(Frame_Handler.get_frame(grayscale=False), "menu_lab_top.png") # the research running and its time
            
            # Find assistant available label
            xys = Frame_Handler.locate(self._get_assistant_available_template(), thresh=0.8, return_all=True)
            xys = sorted(xys, key=lambda pair: pair[1])
            if len(xys) == 0: return False
            x, y = xys[0]
            if x is None or y is None: return False
            
            Input_Handler.click(x, y)
            time.sleep(0.5)
            
            # Find assign assistant label
            xys = Frame_Handler.locate(self.assets["assign_assistant"], thresh=0.9, grayscale=False, return_all=True)
            if len(xys) == 0: return False
            
            x, y = sorted(xys, key=lambda pair: pair[1])[0]
            if x is None or y is None: return False
            
            Input_Handler.click(x, y)
            time.sleep(0.5)
            
            # Find confirm button
            x, y = Frame_Handler.locate(self.assets["confirm_assistant"], grayscale=False, thresh=0.9)
            if x is None or y is None: return False
            
            Input_Handler.click(x, y)
            time.sleep(0.5)
            return True
        except (KeyboardInterrupt, SystemExit): raise
        except Exception:
            logger.exception("Upgrader.assign_lab_assistant:")
    
    @require_exit(x=0.99, y=0.01)
    def pet_house_upgrade(self):
        priority = [] if Task_Handler.excluded("pet_house_priority") else configs.PET_HOUSE_UPGRADE_PRIORITY
        return self._menu_upgrade("pet", priority)
    
    @require_exit(x=0.99, y=0.01)
    def builder_random_upgrade(self):
        import time, re, numpy as np
        
        try:
            # Open upgrade list menu
            self._click_build_button()
            time.sleep(0.5)
            self._click_builder_builders()
            time.sleep(0.5)
            
            # Locate menu boundaries
            sug_template = self._get_suggested_upgrade_template()
            x_sug, y_sug = Frame_Handler.locate(sug_template, thresh=0.70, grayscale=True, prefilter=True)
            if x_sug is None or y_sug is None: return None
            frame = Frame_Handler.get_frame(grayscale=False, use_cached=True)
            menu, menu_left, menu_top, menu_right, menu_bottom = self._get_upgrade_menu(frame, return_bounds=True)
            menu_center = (menu_left + menu_right) / 2
            if configs.START_FROM_MENU_TOP:
                Input_Handler.swipe_up(x=menu_center, y1=y_sug, y2=menu_top, duration=0, hold_end_time=100)
            else:
                self._scroll_to_menu_bottom(menu_left, menu_right, menu_top, menu_bottom)
            
            def locate_upgrade():
                frame = Frame_Handler.get_frame(grayscale=False)
                menu = Frame_Handler.crop(frame, menu_left, menu_top, menu_right, menu_bottom)
                # x_sug, y_sug = Frame_Handler.locate(sug_template, frame, thresh=0.70, grayscale=True, prefilter=True)

                # Find a valid upgrade
                potential_y_locs = self._get_potential_upgrade_locs(menu, exclude_new=True)
                if len(potential_y_locs) == 0: return None, None
                potential_y_locs = potential_y_locs / WINDOW_DIMS[1] + menu_top
                # if y_sug is not None: potential_y_locs = potential_y_locs[potential_y_locs > y_sug]
                
                # Determine discounted upgrades
                discounted_upgrades = []
                # discounted_locs = Frame_Handler.locate(self.assets["green_tag"], menu, thresh=0.80, grayscale=False, return_all=True, normalize=False)
                # for x, y in discounted_locs:
                #     if len(potential_y_locs) == 0: break
                #     if x is None or y is None: continue
                #     y_global = y / WINDOW_DIMS[1] + menu_top
                #     min_idx = np.argmin(abs(potential_y_locs - y_global))
                #     if abs(potential_y_locs[min_idx] - y_global) < 0.02:
                #         discounted_upgrades.append(potential_y_locs[min_idx])
                #         potential_y_locs = np.delete(potential_y_locs, min_idx)

                # Choose an upgrade
                if len(discounted_upgrades) > 0:
                    return menu_center, np.random.choice(discounted_upgrades)
                return menu_center, np.random.choice(potential_y_locs)
            
            x_upgrade, y_upgrade = self._scroll_locate_upgrade(
                locate_upgrade,
                menu_left,
                menu_right,
                menu_top,
                menu_bottom,
                dir="down" if configs.START_FROM_MENU_TOP else "up",
            )
            if x_upgrade is None or y_upgrade is None: return None
            
            # Get upgrade name
            section = Frame_Handler.get_frame_section(menu_left, y_upgrade - 0.025, menu_center, y_upgrade + 0.025, high_contrast=True)
            upgrade_name = spell_check(re.sub(r"\s*x\d+$", "", OCR_Handler.get_text(section)[0].lower()), ["buildings/builder-base", "traps/builder-base"], phrase_level=True)
            
            # Try to click upgrade button (only for walls)
            self._click_upgrade(0.5)
            time.sleep(0.5)
            
            # Select upgrade
            Input_Handler.click(x_upgrade, y_upgrade)
            
            # Click confirm button
            if not self._click_builder_confirm(): return None
            time.sleep(0.5)
            return upgrade_name
        except (KeyboardInterrupt, SystemExit): raise
        except Exception:
            logger.exception("Upgrader.builder_random_upgrade:")
            return None
    
    @require_exit(x=0.99, y=0.01)
    def builder_specified_upgrade(self, upgrade_text):
        import time, numpy as np
        
        try:
            # Render templates
            if type(upgrade_text) == str: upgrade_text = [upgrade_text]
            if len(upgrade_text) == 0: return None
            templates = self._get_upgrade_templates(upgrade_text, include_new=False)
            combined = list(zip(templates, upgrade_text))
            np.random.shuffle(combined)
            templates, upgrade_text = zip(*combined)
            
            # Open upgrade list menu
            self._click_build_button()
            time.sleep(0.5)
            self._click_builder_builders()
            time.sleep(0.5)
            
            # Find suggested upgrades label
            sug_template = self._get_suggested_upgrade_template()
            x_sug, y_sug = Frame_Handler.locate(sug_template, thresh=0.70, grayscale=True, prefilter=True)
            if x_sug is None or y_sug is None: return None
            frame = Frame_Handler.get_frame(grayscale=False, use_cached=True)
            menu, menu_left, menu_top, menu_right, menu_bottom = self._get_upgrade_menu(frame, return_bounds=True)
            menu_center = (menu_left + menu_right) / 2

            # Move ongoing upgrades out of view
            if configs.START_FROM_MENU_TOP:
                Input_Handler.swipe_up(x=menu_center, y1=y_sug, y2=menu_top, duration=0, hold_end_time=100)
            else:
                self._scroll_to_menu_bottom(menu_left, menu_right, menu_top, menu_bottom)
            
            # Find upgrade text
            def locate_upgrade():
                frame = Frame_Handler.get_frame(grayscale=False)
                x_sug, y_sug = Frame_Handler.locate(sug_template, frame, thresh=0.70, grayscale=True, prefilter=True)
                xys = Frame_Handler.batch_locate(templates, frame, thresh=0.80, ref="lc", grayscale=True)
                non_discounted_upgrades = []
                for (x, y), name in zip(xys, upgrade_text):
                    if (
                        x is not None and y is not None
                        and (y_sug is None or (y_sug is not None and y > y_sug))
                        and y + 0.025 < menu_bottom
                    ):
                        section = Frame_Handler.crop(frame, menu_left, y, menu_right, y+0.025)
                        sufficient_resources = self._get_sufficient_resources(section)
                        if sufficient_resources:
                            non_discounted_upgrades.append((x, y, name))
                            continue
                            
                            # Or if it is aligned to green discount tag
                            tag_x, tag_y = Frame_Handler.locate(self.assets["green_tag"], section, thresh=0.80, grayscale=False, ref="rc", normalize=False)
                            if tag_x is not None and tag_y is not None and abs(x - (menu_left + tag_x/WINDOW_DIMS[1])) < 0.02:
                                return x, y, name # Prioritize discounted upgrades

                if len(non_discounted_upgrades) > 0:
                    return non_discounted_upgrades[0]
                return None, None, None
            
            x, y, upgrade_name = self._scroll_locate_upgrade(
                locate_upgrade,
                menu_left,
                menu_right,
                menu_top,
                menu_bottom,
                dir="down" if configs.START_FROM_MENU_TOP else "up"
            )
            
            if x is None or y is None: return None
            Input_Handler.click(x, y)
            time.sleep(0.5)
            
            # Try to click upgrade button (only for walls)
            self._click_upgrade(0.5)
            time.sleep(0.5)
            
            # Click confirm button
            if not self._click_builder_confirm(): return None
            time.sleep(0.5)
            return upgrade_name
        except (KeyboardInterrupt, SystemExit): raise
        except Exception:
            logger.exception("Upgrader.builder_specified_upgrade:")
            return None
    
    @require_exit(x=0.99, y=0.01)
    def builder_upgrade(self):
        if not Task_Handler.excluded("builder_base_priority"):
            for priority_level in configs.BUILDER_BASE_UPGRADE_PRIORITY:
                upgrade_name = self.builder_specified_upgrade(priority_level)
                if upgrade_name is not None: return upgrade_name
        return self.builder_random_upgrade()
    
    @require_exit(x=0.99, y=0.01)
    def builder_lab_random_upgrade(self):
        import time, re, numpy as np
        
        try:
            # Open lab upgrade list menu
            self._click_build_button()
            time.sleep(0.5)
            self._click_builder_lab()
            time.sleep(0.5)
            
            # Locate menu boundaries
            sug_template = self._get_suggested_upgrade_template()
            x_sug, y_sug = Frame_Handler.locate(sug_template, thresh=0.70, grayscale=True, prefilter=True)
            if x_sug is None or y_sug is None: return None
            frame = Frame_Handler.get_frame(grayscale=False, use_cached=True)
            menu, menu_left, menu_top, menu_right, menu_bottom = self._get_upgrade_menu(frame, return_bounds=True)
            menu_center = (menu_left + menu_right) / 2
            if configs.START_FROM_MENU_TOP:
                Input_Handler.swipe_up(x=menu_center, y1=y_sug, y2=menu_top, duration=0, hold_end_time=100)
            else:
                self._scroll_to_menu_bottom(menu_left, menu_right, menu_top, menu_bottom)
            
            def locate_upgrade():
                frame = Frame_Handler.get_frame(grayscale=False)
                menu = Frame_Handler.crop(frame, menu_left, menu_top, menu_right, menu_bottom)
                # x_sug, y_sug = Frame_Handler.locate(sug_template, frame, thresh=0.70, grayscale=True, prefilter=True)
                
                # Find a valid upgrade
                potential_y_locs = self._get_potential_upgrade_locs(menu)
                if len(potential_y_locs) == 0: return None, None
                potential_y_locs = potential_y_locs / WINDOW_DIMS[1] + menu_top
                # if y_sug is not None: potential_y_locs = potential_y_locs[potential_y_locs > y_sug]
                
                # Determine discounted upgrades
                discounted_upgrades = []
                # discounted_locs = Frame_Handler.locate(self.assets["green_tag"], menu, thresh=0.80, grayscale=False, return_all=True, normalize=False)
                # for x, y in discounted_locs:
                #     if len(potential_y_locs) == 0: break
                #     if x is None or y is None: continue
                #     y_global = y / WINDOW_DIMS[1] + menu_top
                #     min_idx = np.argmin(abs(potential_y_locs - y_global))
                #     if abs(potential_y_locs[min_idx] - y_global) < 0.02:
                #         discounted_upgrades.append(potential_y_locs[min_idx])
                #         potential_y_locs = np.delete(potential_y_locs, min_idx)

                # Choose an upgrade
                if len(discounted_upgrades) > 0:
                    return menu_center, np.random.choice(discounted_upgrades)
                return menu_center, np.random.choice(potential_y_locs)
            
            x_upgrade, y_upgrade = self._scroll_locate_upgrade(
                locate_upgrade,
                menu_left,
                menu_right,
                menu_top,
                menu_bottom,
                dir="down" if configs.START_FROM_MENU_TOP else "up",
            )
            if x_upgrade is None or y_upgrade is None: return None
            
            # Get upgrade name
            section = Frame_Handler.get_frame_section(menu_left, y_upgrade - 0.025, menu_center, y_upgrade + 0.025, high_contrast=True)
            upgrade_name = spell_check(re.sub(r"\s*x\d+$", "", OCR_Handler.get_text(section)[0].lower()), "troops", phrase_level=True)
            
            # Select upgrade
            Input_Handler.click(x_upgrade, y_upgrade)
            
            # Click confirm button
            if not self._click_builder_confirm(): return None
            time.sleep(0.5)
            return upgrade_name
        except (KeyboardInterrupt, SystemExit): raise
        except Exception:
            logger.exception("Upgrader.builder_lab_random_upgrade:")
            return None
    
    @require_exit(x=0.99, y=0.01)
    def builder_lab_specified_upgrade(self, upgrade_text):
        import time, numpy as np
        
        try:
            # Render templates
            if type(upgrade_text) == str: upgrade_text = [upgrade_text]
            if len(upgrade_text) == 0: return None
            templates = self._get_upgrade_templates(upgrade_text, include_new=True)
            combined = list(zip(templates, upgrade_text))
            np.random.shuffle(combined)
            templates, upgrade_text = zip(*combined)
            
            # Open lab upgrade list menu
            self._click_build_button()
            time.sleep(0.5)
            self._click_builder_lab()
            time.sleep(0.5)
            
            # Find suggested upgrades label
            sug_template = self._get_suggested_upgrade_template()
            x_sug, y_sug = Frame_Handler.locate(sug_template, thresh=0.70, grayscale=True, prefilter=True)
            if x_sug is None or y_sug is None: return None
            frame = Frame_Handler.get_frame(grayscale=False, use_cached=True)
            menu, menu_left, menu_top, menu_right, menu_bottom = self._get_upgrade_menu(frame, return_bounds=True)
            menu_center = (menu_left + menu_right) / 2

            # Move ongoing upgrades out of view
            if configs.START_FROM_MENU_TOP:
                Input_Handler.swipe_up(x=menu_center, y1=y_sug, y2=menu_top, duration=0, hold_end_time=100)
            else:
                self._scroll_to_menu_bottom(menu_left, menu_right, menu_top, menu_bottom)
            
            # Find upgrade text
            def locate_upgrade():
                frame = Frame_Handler.get_frame(grayscale=False)
                x_sug, y_sug = Frame_Handler.locate(sug_template, frame, thresh=0.70, grayscale=True, prefilter=True)
                xys = Frame_Handler.batch_locate(templates, frame, thresh=0.80, ref="lc", grayscale=True)
                non_discounted_upgrades = []
                for (x, y), name in zip(xys, upgrade_text):
                    if (
                        x is not None and y is not None
                        and (y_sug is None or (y_sug is not None and y > y_sug))
                        and y + 0.025 < menu_bottom
                    ):
                        section = Frame_Handler.crop(frame, menu_left, y, menu_right, y+0.025)
                        sufficient_resources = self._get_sufficient_resources(section)
                        if sufficient_resources:
                            non_discounted_upgrades.append((x, y, name))
                            continue
                            
                            # Or if it is aligned to green discount tag
                            tag_x, tag_y = Frame_Handler.locate(self.assets["green_tag"], section, thresh=0.80, grayscale=False, ref="rc", normalize=False)
                            if tag_x is not None and tag_y is not None and abs(x - (menu_left + tag_x/WINDOW_DIMS[1])) < 0.02:
                                return x, y, name # Prioritize discounted upgrades

                if len(non_discounted_upgrades) > 0:
                    return non_discounted_upgrades[0]
                return None, None, None
            
            x, y, upgrade_name = self._scroll_locate_upgrade(
                locate_upgrade,
                menu_left,
                menu_right,
                menu_top,
                menu_bottom,
                dir="down" if configs.START_FROM_MENU_TOP else "up",
            )
            
            if x is None or y is None: return None
            Input_Handler.click(x, y)
            
            # Find confirm button
            if not self._click_builder_confirm(): return None
            time.sleep(0.5)
            return upgrade_name
        except (KeyboardInterrupt, SystemExit): raise
        except Exception:
            logger.exception("Upgrader.builder_lab_specified_upgrade:")
            return None
    
    @require_exit(x=0.99, y=0.01)
    def builder_lab_upgrade(self):
        if not Task_Handler.excluded("builder_lab_priority"):
            for priority_level in configs.BUILDER_LAB_UPGRADE_PRIORITY:
                upgrade_name = self.builder_lab_specified_upgrade(priority_level)
                if upgrade_name is not None: return upgrade_name
        return self.builder_lab_random_upgrade()
    
    # ============================================================
    # 📡 Upgrade Monitoring
    # ============================================================
    
    def run_home_base(self, exclude_base=False, exclude_lab=False, exclude_pet=False, walls=True):
        import time
        
        Input_Handler.zoom(dir="out")
        Input_Handler.swipe_down()
        
        # Building upgrades
        upgrades_started = []
        heroes_on = not Task_Handler.excluded("heroes")
        if not exclude_base or heroes_on:
            # The last hero_builders free builders go to heroes only (MyBot "reserved builders for heroes")
            reserve = int(Settings_Handler.get("home", "hero_builders", 0) or 0) if heroes_on else 0
            counter = 0
            while counter < configs.MAX_UPGRADES_PER_CHECK:
                counter += 1
                try:
                    initial_builders = self.get_home_builders(1)
                    if initial_builders <= max(0, configs.OPEN_HOME_BUILDERS): break
                    heroes_only = exclude_base or initial_builders <= max(0, configs.OPEN_HOME_BUILDERS) + reserve
                    upgraded = self.home_upgrade(heroes_only=heroes_only)
                    time.sleep(0.5)
                    final_builders = self.get_home_builders(1)
                    if upgraded is None or final_builders >= initial_builders: break
                    upgrades_started.append(upgraded.lower())
                    Resource_Reader.read()
                except (KeyboardInterrupt, SystemExit): raise
                except:
                    logger.warning("Encountered an error while attempting to upgrade home base. Retrying...")
        if not Task_Handler.excluded("builder_apprentice") and self._due("apprentice"):
            assigned = self.assign_builder_apprentice()
            if assigned: self._later("apprentice", 12, "Builder apprentice assigned")
            elif assigned is False: self._later("apprentice", 2, "No builder apprentice to assign")

        # Lab upgrades
        lab_upgrades_started = []
        try:
            if not exclude_lab and self.home_lab_available(1):
                before = dict(Resource_Reader.read() or {})
                upgraded = self.home_lab_upgrade()
                time.sleep(0.5)
                final_lab_avail = self.home_lab_available(1)
                if upgraded is not None and not final_lab_avail and self._paid(before, upgraded):
                    lab_upgrades_started.append(upgraded.lower())
        except (KeyboardInterrupt, SystemExit): raise
        except:
            logger.warning("Encountered an error while attempting to upgrade home lab. Retrying...")
        if not Task_Handler.excluded("lab_assistant") and self._due("lab_assistant"):
            assigned = self.assign_lab_assistant()
            if assigned: self._later("lab_assistant", 12, "Lab assistant assigned")
            elif assigned is False: self._later("lab_assistant", 2, "No lab assistant to assign")

        # Pet house upgrades: the pet house takes one at a time and a pet upgrade takes days, so a busy house is not
        # looked at again for hours (its count is only in the build menu)
        pet_upgrades_started = []
        try:
            if not exclude_pet and self._due("pet"):
                if self.pet_house_available(1):
                    before = dict(Resource_Reader.read() or {})
                    upgraded = self.pet_house_upgrade()
                    time.sleep(0.5)
                    final_pet_avail = self.pet_house_available(1)
                    if upgraded is not None and not final_pet_avail:
                        if self._paid(before, upgraded):
                            pet_upgrades_started.append(upgraded.lower())
                            self._later("pet", 12, "Pet upgrade started")
                            pet_busy = True
                        else:
                            self._later("pet", 1, "Pet upgrade did not start")
                            pet_busy = False
                    else:
                        pet_busy = final_pet_avail is False
                        if upgraded is None: self._later("pet", 1, "No pet upgrade to start")
                else:
                    self._later("pet", 6, "Pet house busy")
                    pet_busy = True
                Cache_Manager["status"] = dict(Cache_Manager.get("status") or {}, pet_busy=pet_busy) # for Telegram /ozet
        except (KeyboardInterrupt, SystemExit): raise
        except: pass

        # Builder status (Emre 02.11, 4A): every 2 hours, and again once an upgrade started
        try:
            if upgrades_started or lab_upgrades_started or self._due("status"):
                self.read_status()
                self._later("status", 2, "Status read")
        except (KeyboardInterrupt, SystemExit): raise
        except: logger.exception("Upgrader.read_status:")

        # Walls last, with what the upgrades above left over (when attacking, the bot runs them after the attack instead)
        try:
            if walls:
                Resource_Reader.read()
                self.run_walls()
        except (KeyboardInterrupt, SystemExit): raise
        except:
            logger.warning("Encountered an error while attempting to upgrade walls")

        for kind, started in (("home", upgrades_started), ("home_lab", lab_upgrades_started), ("pet", pet_upgrades_started)):
            for upgrade in started:
                logger.info(f"Started upgrading {upgrade} ({kind})")
                report("upgrade", kind=kind, name=upgrade)
        for upgrade in upgrades_started + lab_upgrades_started + pet_upgrades_started:
            send_notification(f"🔨 Geliştirme başladı: {upgrade}", silent=True)
    
    def run_builder_base(self, exclude_base=False, exclude_lab=False):
        import time
        
        Input_Handler.zoom(dir="out")
        Input_Handler.swipe_down()

        # Building upgrades
        upgrades_started = []
        if not exclude_base:
            counter = 0
            while counter < configs.MAX_UPGRADES_PER_CHECK:
                counter += 1
                try:
                    # 1 s was too short right after the elixir cart window: "Failed to get builder builders"
                    initial_builders = self.get_builder_builders(5)
                    if initial_builders <= max(0, configs.OPEN_BUILDER_BUILDERS): break
                    upgraded = self.builder_upgrade()
                    time.sleep(0.5)
                    final_builders = self.get_builder_builders(5)
                    if upgraded is not None:
                        upgraded = upgraded.lower()
                        if final_builders < initial_builders: upgrades_started.append(upgraded)
                        elif final_builders == initial_builders and upgraded != "wall": break
                    else: break
                except (KeyboardInterrupt, SystemExit): raise
                except:
                    logger.warning("Encountered an error while attempting to upgrade builder base. Retrying...")
        
        # Lab upgrades
        lab_upgrades_started = []
        try:
            if not exclude_lab and self.builder_lab_available(1):
                upgraded = self.builder_lab_upgrade()
                time.sleep(0.5)
                final_lab_avail = self.builder_lab_available(1)
                if upgraded is not None and not final_lab_avail: lab_upgrades_started.append(upgraded.lower())
        except (KeyboardInterrupt, SystemExit): raise
        except:
            logger.warning("Encountered an error while attempting to upgrade builder lab. Retrying...")
        
        for kind, started in (("builder", upgrades_started), ("builder_lab", lab_upgrades_started)):
            for upgrade in started:
                logger.info(f"Started upgrading {upgrade} ({kind})")
                report("upgrade", kind=kind, name=upgrade)
        for upgrade in upgrades_started + lab_upgrades_started:
            send_notification(f"🔨 Geliştirme başladı: {upgrade}", silent=True)
