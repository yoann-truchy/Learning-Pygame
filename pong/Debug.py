import pygame
from Constants import DEBUG_LINE_SPACING, WHITE


class Debug_window:
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        if kwargs.get("flags", None) is None:
            kwargs.update({"flags": pygame.SRCALPHA})
        else:
            kwargs.update({"flags": kwargs.get("flags") | pygame.SRCALPHA})

        self.stored_args = args
        self.stored_kwargs = kwargs
        self.surface = pygame.Surface(*args, **kwargs)
        self.rect = self.surface.get_rect()

        self.font = pygame.font.SysFont("Calibri", 16)

        # size
        self.needed_heigh = 0
        self.max_width = 0

        # variables for dragging
        self.is_dragged = False
        self.dragging_x_offset = 0
        self.dragging_y_offset = 0

    def drag_start(self, mouse_pos: tuple):
        self.is_dragged = True
        self.dragging_x_offset = self.rect.x - mouse_pos[0]
        self.dragging_y_offset = self.rect.y - mouse_pos[1]

    def drag_stop(self):
        self.is_dragged = False

    def drag_at(self, mouse_pos: tuple):
        self.rect.x = mouse_pos[0] + self.dragging_x_offset
        self.rect.y = mouse_pos[1] + self.dragging_y_offset

    def resize_surface(self, width: int, height: int):
        """change the size of the surface"""
        self.max_width = width
        self.max_heigh = height

        old_pos = self.rect.topleft

        self.surface = pygame.Surface((width, height), **self.stored_kwargs)
        self.rect = self.surface.get_rect()
        self.rect.topleft = old_pos

    def render_lines(
        self,
        debug_lines: list[str],
        screen: pygame.surface,
        line_space: int = DEBUG_LINE_SPACING,
    ):
        # clear surface
        self.surface.fill((0, 0, 0, 75))

        new_max_width = 0
        text_height_summ = 0
        # draw lines
        blit_sequence = tuple()
        for i, debug_line_txt in enumerate(debug_lines):
            line_y_position = 10 + DEBUG_LINE_SPACING * i
            line_position = (10, line_y_position)

            text_object = self.font.render(str(debug_line_txt), False, WHITE)
            blit_sequence = (*blit_sequence, (text_object, line_position))

            txt_w, txt_h = self.font.size(str(debug_line_txt))
            text_height_summ += txt_h
            new_max_width = max(new_max_width, txt_w)

        # dinamycly change the surface size based on the text size
        if new_max_width > self.max_width:
            # calculate total height
            total_lines = len(debug_lines)
            total_height = text_height_summ + (
                (DEBUG_LINE_SPACING - text_height_summ / total_lines)
                * (total_lines - 1)
            )
            self.resize_surface(20 + new_max_width, 20 + total_height)

        self.surface.blits(blit_sequence)
        screen.blit(self.surface, self.rect)
