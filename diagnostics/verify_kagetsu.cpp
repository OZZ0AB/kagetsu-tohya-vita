// SPDX-License-Identifier: GPL-2.0-or-later
// Read-only compatibility check against local PC data, using production readers.
#include "NsaReader.h"
#include "ScriptHandler.h"
#include "sjis2utf16.h"
#include <cassert>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

SJIS2UTF16 encoding;
Coding2UTF16 *coding2utf16 = &encoding;

int main(int argc, char **argv)
{
    if (argc != 2) return 2;
    encoding.init();
    std::string root = std::string(argv[1]) + "/";
    ScriptHandler script;
    script.reset();
    assert(script.openScript(&root[0]) == 0);
    assert(script.screen_width == 640 && script.screen_height == 480);
    const char *labels[] = {"define", "start", "loaded", "set_window_mm", "imagemode"};
    for (const char *label : labels) assert(script.lookupLabel(label).label_header);

    // Exercise English dialogue tokens throughout the complete supplied script.
    char *line = script.getAddress(0);
    unsigned text_lines = 0;
    while (*line) {
        char *end = std::strchr(line, '\n');
        if (!end) break;
        char *start = line;
        while (*start == ' ' || *start == '\t') ++start;
        if (*start == '`') {
            script.setCurrent(start);
            script.readToken();
            assert(script.isText());
            assert(script.getEndStatus() & ScriptHandler::END_1BYTE_CHAR);
            assert(script.getNext() <= end + 1);
            ++text_lines;
        }
        line = end + 1;
    }
    assert(text_lines > 22000);

    NsaReader files(0, &root[0], BaseReader::ARCHIVE_TYPE_NSA | BaseReader::ARCHIVE_TYPE_NS2);
    assert(files.open() == 0);
    const int count = files.getNumFiles();
    assert(count > 1100);
    int compressed = 0;
    for (int i = 0; i < count; ++i) {
        BaseReader::FileInfo info = files.getFileByIndex(i);
        const size_t length = files.getFileLength(info.name);
        assert(length > 0 && length < 16 * 1024 * 1024);
        std::vector<unsigned char> bytes(length);
        int location = 0;
        assert(files.getFile(info.name, bytes.data(), &location) == length);
        assert(location == BaseReader::ARCHIVE_TYPE_NSA);
        if (info.compression_type != BaseReader::NO_COMPRESSION) ++compressed;
    }
    const char *images[] = {"image\\word\\type_moon.jpg", "image\\add\\tuxxx.jpg",
                            "image\\title\\kagetsu_title01_en.jpg", "image\\title\\kagetsu_title02_en.jpg"};
    for (const char *name : images) {
        const size_t length = files.getFileLength(name);
        assert(length > 2);
        std::vector<unsigned char> bytes(length);
        assert(files.getFile(name, bytes.data()) == length);
        assert(bytes[0] == 0xff && bytes[1] == 0xd8);
    }
    // Lower-case 'cd' mirrors the native CD playback path; the folder is 'CD'.
    for (int track = 2; track <= 18; ++track) {
        char path[64];
        std::snprintf(path, sizeof(path), "cd\\track%02d.ogg", track);
        const size_t length = files.getFileLength(path);
        assert(length > 4);
        std::vector<unsigned char> bytes(length);
        assert(files.getFile(path, bytes.data()) == length);
        assert(std::memcmp(bytes.data(), "OggS", 4) == 0);
    }
    assert(files.getFileLength("default.ttf") > 1024);
    std::printf("Production readers: 640x480, %u English dialogue lines, %d archive entries (%d compressed), startup art, font, all 17 CD tracks: OK\n",
                text_lines, count, compressed);
}
