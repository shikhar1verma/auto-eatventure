class Constants:
    """Coordinate dicts built from a ScaledCoords instance.

    All callers that previously used module-level `loc.xxx` now use
    an instance: `self.loc = Constants(sc)` then `self.loc.xxx`.
    """

    def __init__(self, sc):
        self.close_nofication_coords = {
            'x': sc.close_notification_x,
            'y': sc.close_notification_y
        }

        self.first_lemonade_stand_open_coords = {
            'x': sc.first_lemonade_stand_open_x,
            'y': sc.first_lemonade_stand_open_y
        }

        self.settings_coords = {
            'x': sc.settings_x,
            'y': sc.settings_y
        }

        self.cloud_save_coords = {
            'x': sc.cloud_save_x,
            'y': sc.cloud_save_y
        }

        self.email_input_coords = {
            'x': sc.email_input_x,
            'y': sc.email_input_y
        }

        self.password_input_coords = {
            'x': sc.password_input_x,
            'y': sc.password_input_y,
        }

        self.text_ok_button_coords = {
            'x': sc.text_ok_button_x,
            'y': sc.text_ok_button_y,
        }

        self.login_button_coords = {
            'x': sc.login_button_x,
            'y': sc.login_button_y
        }

        self.use_cloud_save_button_coords = {
            'x': sc.use_cloud_save_button_x,
            'y': sc.use_cloud_save_button_y
        }

        self.close_game_for_restart_button_coords = {
            'x': sc.close_game_for_restart_x,
            'y': sc.close_game_for_restart_y
        }

        self.close_offline_earnings_coords = {
            'x': sc.close_offline_earnings_x,
            'y': sc.close_offline_earnings_y
        }

        self.upgrade_button_coords = {
            'x': sc.upgrade_button_x,
            'y': sc.upgrade_button_y
        }

        self.single_upgrade_button_coords = {
            'x': sc.single_upgrade_button_x,
            'y': sc.single_upgrade_button_y
        }

        self.close_upgrade_button_coords = {
            'x': sc.close_upgrade_button_x,
            'y': sc.close_upgrade_button_y
        }

        self.next_level_button_coords = {
            'x': sc.next_level_button_x,
            'y': sc.next_level_button_y
        }

        self.renovate_button_coords = {
            'x': sc.renovate_button_x,
            'y': sc.renovate_button_y
        }

        self.ads_button_coords = {
            'x': sc.ads_button_x,
            'y': sc.ads_button_y
        }

        self.fly_next_city_button_coords = {
            'x': sc.fly_next_city_button_x,
            'y': sc.fly_next_city_button_y
        }

        self.welcome_city_ok_button_coords = {
            'x': sc.welcome_city_ok_button_x,
            'y': sc.welcome_city_ok_button_y
        }

        self.null_click_coords = {
            'x': sc.null_click_x,
            'y': sc.null_click_y
        }

        self.chest_coords = {
            'x': sc.chest_x,
            'y': sc.chest_y
        }

        self.close_chest_button_coords = {
            'x': sc.close_chest_button_x,
            'y': sc.close_chest_button_y
        }

        self.swipe_layout_down_coords = {
            'start': {
                'x': sc.swipe_layout_down_start_x,
                'y': sc.swipe_layout_down_start_y
            },
            'end': {
                'x': sc.swipe_layout_down_end_x,
                'y': sc.swipe_layout_down_end_y
            }
        }

        self.swipe_layout_up_coords = {
            'start': {
                'x': sc.swipe_layout_up_start_x,
                'y': sc.swipe_layout_up_start_y
            },
            'end': {
                'x': sc.swipe_layout_up_end_x,
                'y': sc.swipe_layout_up_end_y
            }
        }

        self.swipe_layout_little_up_coords = {
            'start': {
                'x': sc.swipe_layout_little_up_start_x,
                'y': sc.swipe_layout_little_up_start_y
            },
            'end': {
                'x': sc.swipe_layout_little_up_end_x,
                'y': sc.swipe_layout_little_up_end_y
            }
        }

        self.danger_max_y = sc.danger_max_y

        self.swipe_layout_little_down_coords = {
            'start': {
                'x': sc.swipe_layout_little_down_start_x,
                'y': sc.swipe_layout_little_down_start_y
            },
            'end': {
                'x': sc.swipe_layout_little_down_end_x,
                'y': sc.swipe_layout_little_down_end_y
            }
        }
