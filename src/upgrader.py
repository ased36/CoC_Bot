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
        return click_with_timeout(
            lambda: Frame_Handler.locate(self.assets["confirm"], grayscale=False, thresh=0.85, use_cached=True),
            timeout=timeout
        )

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
        band = Frame_Handler.crop(frame, left, y - self.NAME_DY - 0.02, 1.0, y + 0.02)
        return Frame_Handler.locate(self.assets["green_tag"], band, thresh=0.80, grayscale=False, normalize=False) != (None, None)

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

    def _choose_row(self, rows, priority, blocked):
        """Discounted first, then the priority list, then cheapest (or random); Town Hall only when nothing else fits."""
        import random
        eligible = [
            r for r in rows
            if r["affordable"] and not r["new"] and r["cost"] is not None
            and not (r["names"] & blocked) and self._keeps_minimum(r)
        ]
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
    def _menu_upgrade(self, kind, priority):
        """Start one upgrade from the home builders (kind "home"), laboratory ("lab") or pet house ("pet") menu."""
        import time

        try:
            blocked = {}
            if kind == "home":
                blocked = self._home_blocked_names()
                if not Settings_Handler.get("home", "town_hall", True): blocked["town hall"] = "Town Hall"
            names = sorted({name for level in priority for name in level} | set(blocked.values()) | ({"Town Hall"} if kind == "home" else set()))

            start = time.time()
            bounds = self._open_menu(kind)
            if bounds is None: return None
            rows, page = self._scan_menu(kind, bounds, names)
            row, reason = self._choose_row(rows, priority, set(blocked))
            affordable = [r for r in rows if r["affordable"]]
            unread = sum(1 for r in affordable if r["cost"] is None)
            logger.info(f"Menu {kind}: {len(rows)} rows, {len(affordable)} affordable, {unread} unread, {int(time.time() - start)}s")
            if row is None:
                logger.info(f"No upgrade fits ({kind})")
                return None
            cost = f"{row['cost']:,}".replace(",", ".")
            logger.info(f"Chosen ({reason}): {row['resource']} {cost}{' discounted' if row['discount'] else ''}")
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
    def home_upgrade(self):
        priority = [] if Task_Handler.excluded("home_base_priority") else configs.HOME_BASE_UPGRADE_PRIORITY
        return self._menu_upgrade("home", priority)

    # ============================================================
    # 🧱 Walls (no builder needed, upgrade instantly)
    # ============================================================

    def _wall_payment(self, cost):
        """Pay with elixir first, then gold, only if the panel minimum still remains after paying."""
        last = Resource_Reader.last
        for resource, key in (("elixir", "min_elixir"), ("gold", "min_gold")):
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

    @require_exit(x=0.99, y=0.01)
    def wall_upgrade(self):
        """Upgrade the cheapest wall that leaves the panel minimums. Returns the resource paid, or None."""
        import time

        try:
            bounds = self._open_menu("home")
            if bounds is None: return None
            rows, page = self._scan_menu("home", bounds, ["Wall"])
            walls = [r for r in rows if "wall" in r["names"] and r["affordable"] and r["cost"] is not None]
            if not walls:
                logger.info(f"No affordable wall in the menu ({len(rows)} rows read)")
                return None
            walls = [r for r in walls if self._wall_payment(r["cost"]) is not None]
            if not walls:
                last = Resource_Reader.last
                fmt = lambda v: "-" if v is None else f"{v:,}".replace(",", ".")
                logger.info(f"Walls skipped: gold {fmt(last.get('gold'))} min {fmt(Settings_Handler.get('walls', 'min_gold', 0))}, elixir {fmt(last.get('elixir'))} min {fmt(Settings_Handler.get('walls', 'min_elixir', 0))}")
                return None
            row = min(walls, key=lambda r: r["cost"])
            resource = self._wall_payment(row["cost"])
            if not self._goto_row("home", bounds, row, page): return None
            if not self._click_wall_button(resource):
                logger.warning(f"Wall {resource} button not found")
                return None
            time.sleep(0.5)
            if self.dry_run:
                cost = f"{row['cost']:,}".replace(",", ".")
                logger.info(f"Dry run, not confirming: wall with {resource} {cost}")
                return None
            if not self._click_home_confirm(): return None
            time.sleep(0.5)
            return resource
        except (KeyboardInterrupt, SystemExit): raise
        except Exception:
            logger.exception("Upgrader.wall_upgrade:")
            return None

    def run_walls(self):
        import time
        if not Settings_Handler.get("walls", "enabled", False):
            logger.info("Walls skipped: disabled")
            return
        for _ in range(Settings_Handler.get("walls", "max_per_round", 5)):
            before = Resource_Reader.last
            resource = self.wall_upgrade()
            if resource is None: break
            time.sleep(0.5)
            after = Resource_Reader.read() or {}
            # Walls finish instantly, so a wall counts only if the resource actually went down
            if (after.get(resource) or 0) >= (before.get(resource) or 0): break
            logger.info("Upgraded wall")
            report("wall")

    @require_exit(x=0.99, y=0.01)
    def assign_builder_apprentice(self):
        import time
        
        try:
            # Open upgrade list menu
            self._click_build_button()
            time.sleep(0.5)
            self._click_home_builders()
            time.sleep(0.5)
            
            # Find assistant available label
            xys = Frame_Handler.locate(self._get_assistant_available_template(), thresh=0.8, return_all=True)
            xys = sorted(xys, key=lambda pair: pair[1])
            if len(xys) == 0: return
            x, y = xys[0]
            if x is None or y is None: return

            Input_Handler.click(x, y)
            time.sleep(0.5)
            
            # Find assign assistant label
            xys = Frame_Handler.locate(self.assets["assign_assistant"], thresh=0.9, grayscale=False, return_all=True)
            if len(xys) == 0: return
            
            x, y = sorted(xys, key=lambda pair: pair[1])[0]
            if x is None or y is None: return
            
            Input_Handler.click(x, y)
            time.sleep(0.5)
            
            # Find confirm button
            x, y = Frame_Handler.locate(self.assets["confirm_assistant"], grayscale=False, thresh=0.9)
            if x is None or y is None: return
            
            Input_Handler.click(x, y)
            time.sleep(0.5)
        except (KeyboardInterrupt, SystemExit): raise
        except Exception:
            logger.exception("Upgrader.assign_builder_apprentice:")
    
    @require_exit(x=0.99, y=0.01)
    def home_lab_upgrade(self):
        priority = [] if Task_Handler.excluded("home_lab_priority") else configs.HOME_LAB_UPGRADE_PRIORITY
        return self._menu_upgrade("lab", priority)

    @require_exit(x=0.99, y=0.01)
    def assign_lab_assistant(self):
        import time
        
        try:
            # Open upgrade list menu
            self._click_build_button()
            time.sleep(0.5)
            self._click_home_lab()
            time.sleep(0.5)
            
            # Find assistant available label
            xys = Frame_Handler.locate(self._get_assistant_available_template(), thresh=0.8, return_all=True)
            xys = sorted(xys, key=lambda pair: pair[1])
            if len(xys) == 0: return
            x, y = xys[0]
            if x is None or y is None: return
            
            Input_Handler.click(x, y)
            time.sleep(0.5)
            
            # Find assign assistant label
            xys = Frame_Handler.locate(self.assets["assign_assistant"], thresh=0.9, grayscale=False, return_all=True)
            if len(xys) == 0: return
            
            x, y = sorted(xys, key=lambda pair: pair[1])[0]
            if x is None or y is None: return
            
            Input_Handler.click(x, y)
            time.sleep(0.5)
            
            # Find confirm button
            x, y = Frame_Handler.locate(self.assets["confirm_assistant"], grayscale=False, thresh=0.9)
            if x is None or y is None: return
            
            Input_Handler.click(x, y)
            time.sleep(0.5)
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
    
    def run_home_base(self, exclude_base=False, exclude_lab=False, exclude_pet=False):
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
                    initial_builders = self.get_home_builders(1)
                    if initial_builders <= max(0, configs.OPEN_HOME_BUILDERS): break
                    upgraded = self.home_upgrade()
                    time.sleep(0.5)
                    final_builders = self.get_home_builders(1)
                    if upgraded is None or final_builders >= initial_builders: break
                    upgrades_started.append(upgraded.lower())
                    Resource_Reader.read()
                except (KeyboardInterrupt, SystemExit): raise
                except:
                    logger.warning("Encountered an error while attempting to upgrade home base. Retrying...")
        if not Task_Handler.excluded("builder_apprentice"):
            self.assign_builder_apprentice()
        
        # Lab upgrades
        lab_upgrades_started = []
        try:
            if not exclude_lab and self.home_lab_available(1):
                upgraded = self.home_lab_upgrade()
                time.sleep(0.5)
                final_lab_avail = self.home_lab_available(1)
                if upgraded is not None and not final_lab_avail: lab_upgrades_started.append(upgraded.lower())
        except (KeyboardInterrupt, SystemExit): raise
        except:
            logger.warning("Encountered an error while attempting to upgrade home lab. Retrying...")
        if not Task_Handler.excluded("lab_assistant"):
            self.assign_lab_assistant()
        
        # Pet house upgrades
        pet_upgrades_started = []
        try:
            if not exclude_pet and self.pet_house_available(1):
                upgraded = self.pet_house_upgrade()
                time.sleep(0.5)
                final_pet_avail = self.pet_house_available(1)
                if upgraded is not None and not final_pet_avail: pet_upgrades_started.append(upgraded.lower())
        except (KeyboardInterrupt, SystemExit): raise
        except: pass

        # Walls last, with what the upgrades above left over
        try:
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
            send_notification(f"Started upgrading {upgrade}")
    
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
            send_notification(f"Started upgrading {upgrade}")
