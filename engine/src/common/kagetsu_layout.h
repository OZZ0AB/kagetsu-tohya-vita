// SPDX-License-Identifier: GPL-2.0-or-later
#ifndef KAGETSU_LAYOUT_H
#define KAGETSU_LAYOUT_H

#include "dialogue_size.h"

namespace tsukihime {

// English 0.5.3 increased the body font to 20px but retained 21 rows.
// Keep that font and reserve room for the click cursor at every size.
inline DialogueSize kagetsuDialogueSize(int level, bool compact = false)
{
    if (level < 0 || level > 3) level = 0;
    const int font = 20 + level * 2;
    const int width = compact ? 514 : 612;
    const int height = compact ? 132 : 441;
    const DialogueSize result = {font, font, font + 4,
                                width / font, (height - font) / (font + 4)};
    return result;
}

} // namespace tsukihime
#endif
