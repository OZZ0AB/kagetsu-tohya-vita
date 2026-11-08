// SPDX-License-Identifier: GPL-2.0-or-later
#include "FontInfo.h"
#include "kagetsu_layout.h"
#include "english_word_wrap.h"
#include <cassert>
#include <cstdio>
#include <string>

static void sourceWindow(FontInfo &font, bool compact)
{
    font.top_xy[0] = compact ? 110 : 18;
    font.top_xy[1] = compact ? 329 : 18;
    font.num_xy[0] = 30;
    font.num_xy[1] = 21;
    font.font_size_xy[0] = font.font_size_xy[1] = 20;
    font.pitch_xy[0] = 20;
    font.pitch_xy[1] = 24;
}

int main()
{
    std::string input;
    for (int i = 0; i < 80; ++i) input += "Every word remains visible on the screen. ";
    input += std::string(100, 'x');
    for (bool compact : {false, true}) {
        FontInfo font;
        sourceWindow(font, compact);
        assert(font.dialogueSizeLevel() == 0);
        for (int level = 0; level < 4; ++level) {
            assert(font.setDialogueSize(level));
            assert(font.dialogueSizeLevel() == level);
            assert(font.font_size_xy[0] == 20 + 2 * level);
            const auto size = tsukihime::kagetsuDialogueSize(level, compact);
            int column = 0, row = 0, pages = 1;
            std::string observed;
            for (std::size_t offset = 0; offset < input.size();) {
                const auto wrap = tsukihime::englishWordWrap(input.c_str(), offset, column, size.columns * 2, 0);
                if (wrap.new_line) {
                    observed += input.substr(offset, wrap.skip_spaces);
                    offset += wrap.skip_spaces;
                    column = 0;
                    row += 2;
                }
                if (tsukihime::dialogueNeedsPage(column, row, size.columns, size.rows)) {
                    column = row = 0;
                    ++pages;
                    continue;
                }
                if (column >= size.columns * 2) { column = 0; row += 2; }
                assert(row / 2 < size.rows);
                assert(font.top_xy[0] + (column + 1) * size.pitch_x / 2 <= (compact ? 624 : 630));
                assert(font.top_xy[1] + row / 2 * size.pitch_y + size.font <= (compact ? 460 : 459));
                observed += input[offset++];
                ++column;
            }
            assert(observed == input && pages > 1);
            std::printf("%s level %d: %d px, %d columns, %d rows, %d pages, text preserved\n",
                        compact ? "Compact" : "Main", level, size.font, size.columns * 2, size.rows, pages);
        }
        assert(font.setDialogueSize(0) && font.dialogueSizeLevel() == 0);
    }
    FontInfo staff;
    sourceWindow(staff, false);
    staff.num_xy[0] = 18;
    assert(staff.dialogueSizeLevel() == -1 && !staff.setDialogueSize(3));
    assert(tsukihime::nextDialogueSize(3) == 0);
    std::puts("Production FontInfo: source normalization, all four sizes, screen bounds and pagination: OK");
}
