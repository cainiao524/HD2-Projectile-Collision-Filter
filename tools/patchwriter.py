"""Writes a stingray patch archive (<archive>.patch_N, .gpu_resources, .stream), the form HellForge and the game load a
mod's resources in. Layout as HD2SDK-CommunityEdition's StreamToc.Serialize writes it:

  header 72 B   magic 0xF0000011, type count, file count, u32 unknown, 56 bytes (copied from a base archive, else 0)
  types  32 B   u64 0, u64 type, u64 file count, u32 16, u32 64
  files  80 B   u64 name, u64 type, u64 main offset, u64 stream offset, u64 gpu offset, u64 0, u64 0,
                u32 main size, u32 stream size, u32 gpu size, u32 16, u32 64, u32 index (1-based, in type order)
  main data     back to back after the file rows; the main file is padded to at least 256 B per file
  gpu, stream   each resource at a 64-byte boundary

  write_patch(path, [(type16, name16, main, stream, gpu), ...], header_tail=None)
"""
import os, struct


def write_patch(path, resources, header_tail=None, unknown=0):
    by_type = {}
    for typ, name, main, stream, gpu in resources:
        by_type.setdefault(int(typ, 16), {})[int(name, 16)] = (main or b"", stream or b"", gpu or b"")
    types = list(by_type)
    nfiles = sum(len(v) for v in by_type.values())
    tail = (header_tail or b"\0" * 56)[:56].ljust(56, b"\0")
    head = struct.pack("<IIII", 0xF0000011, len(types), nfiles, unknown) + tail
    type_rows = b"".join(struct.pack("<QQQII", 0, t, len(by_type[t]), 16, 64) for t in types)
    main_at = len(head) + len(type_rows) + 80 * nfiles
    mains, gpus, streams, rows = bytearray(), bytearray(), bytearray(), []
    index = 1
    for t in types:
        for name, (main, stream, gpu) in by_type[t].items():
            pad = (-(main_at + len(mains))) % 16
            mains += b"\0" * pad
            m_off = main_at + len(mains); mains += main
            g_off = (len(gpus) + 63) // 64 * 64
            if gpu: gpus += b"\0" * (g_off - len(gpus)) + gpu
            s_off = (len(streams) + 63) // 64 * 64
            if stream: streams += b"\0" * (s_off - len(streams)) + stream
            rows.append(struct.pack("<QQQQQQQIIIIII", name, t, m_off, s_off, g_off, 0, 0,
                                    len(main), len(stream), len(gpu), 16, 64, index))
            index += 1
    toc = bytearray(head + type_rows + b"".join(rows) + mains)
    gpus += b"\0" * ((-len(gpus)) % 64)
    streams += b"\0" * ((-len(streams)) % 64)
    if len(toc) < 256 * nfiles:
        toc += b"\0" * (256 * nfiles - len(toc))
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "wb") as f: f.write(toc)
    with open(path + ".gpu_resources", "wb") as f: f.write(gpus)
    with open(path + ".stream", "wb") as f: f.write(streams)
    return nfiles


def header_tail(path):
    """The 56 header bytes after the four u32s of an existing (fat) archive file."""
    with open(path, "rb") as f:
        return f.read(72)[16:72]
