#!/usr/bin/python

import sys

def section_size(sec_id):
    if sec_id > 13 or sec_id < 0:
        raise Exception("Illegal section id {}".format(sec_id))
    if sec_id == 0:
        return 3884
    elif sec_id == 4:
        return 3948
    elif sec_id == 13:
        return 2000
    else:
        return 3968

def compute_checksum(section):
    section_sum = 0

    for i in range(0, len(section), 4):
        to_sum = 0
        for j in range(4):
            to_sum += section[i+j] << (8 * j)

        section_sum = (section_sum + to_sum) & 0xffffffff

    checksum = ((section_sum>>16) + (section_sum & 0xffff)) & 0xffff

    return checksum


def iterate_sections(save):
    for section_num in range(14):
        offset = section_num * 0x1000

        sec_id = 0
        for i in range(2):
            sec_id += save[offset+0xff4+i] << (8 * i)

        sec_size = section_size(sec_id)
        
        checksum = 0
        for i in range(2):
            checksum += save[offset+0xff6+i] << (8 * i)

        save_idx = 0
        for i in range(4):
            save_idx += save[offset+0xffc+i] << (8 * i)

        yield save[offset:offset+sec_size], offset, sec_id, checksum, save_idx

def verify_indices(save, save_num):
    canon_save_idx = None
    canon_sec_id = None

    for section, offset, sec_id, _, save_idx in iterate_sections(save):
        if canon_save_idx == None:
            canon_save_idx = save_idx
            canon_sec_id = sec_id

        if save_idx != canon_save_idx:
            print(f"Inconsistent save index {save_idx} found in section {sec_id} of save {save_num} at offset {offset:x}. (Canonical index {canon_save_idx} established from section {canon_sec_id})")

def verify_checksums(save, save_num):
    for section, offset, sec_id, checksum, _ in iterate_sections(save):
        print(f"Verifying checksum for section {sec_id} of save {save_num} at offset {offset:x}")
        computed_checksum = compute_checksum(section)
        if computed_checksum != checksum:
            print(f"Bad checksum {computed_checksum:x} computed for section {sec_id} of save {save_num} at offset {offset:x}. (Expected {checksum:x})")

def main():
    filename = sys.argv[1]
    with open(filename, "rb") as savefile:
        savebytes = savefile.read()

    saves = (savebytes[:0xe000], savebytes[0xe000:0x1c000])
    halloffame = savebytes[0x1c000:0x1e000]
    mysterygift = savebytes[0x1e000:0x1f000]
    recordedbattle = savebytes[0x1f000:0x20000]

    for index, save in enumerate(saves):
        verify_indices(save, index)
        verify_checksums(save, index)

main()
