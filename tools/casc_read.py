#!/usr/bin/env python3
"""Minimal read-only reader for a local WoW CASC storage: extract files by FileDataID.

Usage: casc_read.py WOW_DIR PRODUCT OUT_DIR FDID [FDID ...]    (or @file with one FDID per line)
  e.g. casc_read.py "/games/World of Warcraft" wowf out 611660 611661

Only opens files under WOW_DIR for reading. Writes OUT_DIR/<fdid> and prints one line per file:
  OK <fdid> <bytes> | MISSING <fdid> <reason> | ENCRYPTED <fdid>

Format notes (public documentation: wowdev.wiki/CASC, /TACT, /BLTE):
  .build.info -> build config (root ckey, encoding ekey) -> Data/data/*.idx map EKeys to
  data.### archives -> BLTE-encoded blobs -> encoding table maps CKey -> EKey -> root (MFST)
  maps FileDataID -> CKey.
"""
import bisect, glob, os, re, struct, sys, zlib
from array import array

LOCALE_ENUS = 0x2
NO_NAME_HASH = 0x10000000


class Encrypted(Exception):
    pass


def blte_decode(data):
    if data[:4] != b"BLTE":
        raise ValueError("not BLTE")
    header_size = struct.unpack_from(">I", data, 4)[0]
    if header_size == 0:
        return decode_chunk(data[8:])
    flags = data[8]
    count = int.from_bytes(data[9:12], "big")
    entry = 24 if flags == 0x0F else 40  # 0x10 = extended chunk info
    sizes, p = [], 12
    for _ in range(count):
        sizes.append(struct.unpack_from(">I", data, p)[0])
        p += entry
    out, pos = bytearray(), header_size
    for size in sizes:
        out += decode_chunk(data[pos:pos + size])
        pos += size
    return bytes(out)


def decode_chunk(chunk):
    mode = chunk[:1]
    if mode == b"N":
        return chunk[1:]
    if mode == b"Z":
        return zlib.decompress(chunk[1:])
    if mode == b"F":
        return blte_decode(chunk[1:])
    if mode == b"E":
        raise Encrypted()
    raise ValueError(f"unsupported BLTE chunk mode {mode!r}")


class Storage:
    def __init__(self, wow_dir, product):
        self.data_dir = os.path.join(wow_dir, "Data", "data")
        self.build_key = self._build_key(wow_dir, product)
        cfg = self._config(os.path.join(wow_dir, "Data", "config"), self.build_key)
        self.index = self._load_indices()
        self.encoding = self._load_encoding(bytes.fromhex(cfg["encoding"].split()[1]))
        root_ckey = bytes.fromhex(cfg["root"].split()[0])
        self.root = self._load_root(self.read_ekey(self.encoding_lookup(root_ckey)))

    # --- configuration -----------------------------------------------------------
    @staticmethod
    def _build_key(wow_dir, product):
        lines = open(os.path.join(wow_dir, ".build.info"), encoding="utf-8").read().splitlines()
        cols = [c.split("!")[0] for c in lines[0].split("|")]
        for line in lines[1:]:
            row = dict(zip(cols, line.split("|")))
            if row.get("Product") == product:
                return row["Build Key"]
        raise SystemExit(f"product {product!r} not in .build.info")

    @staticmethod
    def _config(config_dir, key):
        path = os.path.join(config_dir, key[0:2], key[2:4], key)
        out = {}
        for line in open(path, encoding="utf-8"):
            if " = " in line:
                k, v = line.strip().split(" = ", 1)
                out[k] = v
        return out

    # --- local indices: EKey (first 9 bytes) -> (archive, offset, size) ---------------
    def _load_indices(self):
        latest = {}
        for path in glob.glob(os.path.join(self.data_dir, "*.idx")):
            m = re.fullmatch(r"([0-9a-f]{2})([0-9a-f]{8})\.idx", os.path.basename(path))
            if m:
                bucket, version = m.group(1), int(m.group(2), 16)
                if version > latest.get(bucket, (-1, ""))[0]:
                    latest[bucket] = (version, path)
        index = {}
        for _, path in latest.values():
            blob = open(path, "rb").read()
            hdr_size = struct.unpack_from("<I", blob, 0)[0]
            (version, _bucket, _extra, span_size, span_offs, ekey_len, offset_bits) = struct.unpack_from("<HBBBBBB", blob, 8)
            if version != 7 or (span_size, span_offs, ekey_len) != (4, 5, 9):
                raise ValueError(f"unexpected index format in {path}")
            pos = (8 + hdr_size + 0x0F) & ~0x0F
            entries_size = struct.unpack_from("<I", blob, pos)[0]
            pos += 8
            mask = (1 << offset_bits) - 1
            for p in range(pos, pos + entries_size, 18):
                raw = int.from_bytes(blob[p + 9:p + 14], "big")
                index[blob[p:p + 9]] = (raw >> offset_bits, raw & mask, struct.unpack_from("<I", blob, p + 14)[0])
        return index

    def read_ekey(self, ekey):
        loc = self.index.get(ekey[:9])
        if loc is None:
            raise KeyError("ekey not in local storage")
        archive, offset, size = loc
        with open(os.path.join(self.data_dir, f"data.{archive:03d}"), "rb") as f:
            f.seek(offset)
            blob = f.read(size)
        return blte_decode(blob[30:])  # 30-byte local header precedes the BLTE data

    # --- encoding: CKey -> EKey ----------------------------------------------------------
    def _load_encoding(self, ekey):
        blob = self.read_ekey(ekey)
        if blob[:2] != b"EN":
            raise ValueError("bad encoding file")
        ckey_len, ekey_len = blob[3], blob[4]
        page_kb = struct.unpack_from(">H", blob, 5)[0]
        page_count = struct.unpack_from(">I", blob, 9)[0]
        espec_size = struct.unpack_from(">I", blob, 18)[0]
        table = 22 + espec_size
        first_keys = [blob[table + i * 32: table + i * 32 + ckey_len] for i in range(page_count)]
        return {"blob": blob, "first": first_keys, "pages": table + page_count * 32,
                "page_size": page_kb * 1024, "ck": ckey_len, "ek": ekey_len}

    def encoding_lookup(self, ckey):
        e = self.encoding
        i = bisect.bisect_right(e["first"], ckey) - 1
        if i < 0:
            return None
        blob, pos = e["blob"], e["pages"] + i * e["page_size"]
        end = pos + e["page_size"]
        while pos < end:
            count = blob[pos]
            if count == 0:
                break
            ck = blob[pos + 6:pos + 6 + e["ck"]]
            if ck == ckey:
                return blob[pos + 6 + e["ck"]:pos + 6 + e["ck"] + e["ek"]]
            pos += 6 + e["ck"] + count * e["ek"]
        return None

    # --- root (MFST): FileDataID -> CKey, enUS / all-locale entries ---------------------------
    @staticmethod
    def _load_root(blob):
        if blob[:4] != b"TSFM":
            raise ValueError("unsupported root format (expected MFST)")
        a, b = struct.unpack_from("<II", blob, 4)
        if a == 24 and b in (1, 2):   # 10.1.7+ header: size, version, total, named, pad
            version, pos = b, 24
        else:                          # 8.2 - 10.1.5 header: total, named
            version, pos = 1, 12
        root = {}
        while pos < len(blob):
            if version >= 2:
                n, locale, f1, f2 = struct.unpack_from("<IIII", blob, pos)
                content = f1 | f2 | (blob[pos + 16] << 17)
                pos += 17
            else:
                n, content, locale = struct.unpack_from("<III", blob, pos)
                pos += 12
            deltas = array("i")
            deltas.frombytes(blob[pos:pos + 4 * n])
            if sys.byteorder != "little":
                deltas.byteswap()
            pos += 4 * n
            ckeys_at = pos
            pos += 16 * n
            if not content & NO_NAME_HASH:
                pos += 8 * n
            if not locale & LOCALE_ENUS:
                continue
            fdid = -1
            for i, d in enumerate(deltas):
                fdid += d + 1
                if fdid not in root:
                    root[fdid] = blob[ckeys_at + 16 * i: ckeys_at + 16 * i + 16]
        return root

    def read_fdid(self, fdid):
        ckey = self.root.get(fdid)
        if ckey is None:
            raise KeyError("not in this product's root")
        ekey = self.encoding_lookup(ckey)
        if ekey is None:
            raise KeyError("ckey not in encoding table")
        return self.read_ekey(ekey)


def main():
    wow_dir, product, out_dir = sys.argv[1:4]
    ids = []
    for a in sys.argv[4:]:
        ids += [int(x) for x in open(a[1:]).read().split()] if a.startswith("@") else [int(a)]
    st = Storage(wow_dir, product)
    print(f"# {product} build {st.build_key}: {len(st.root)} files in root, {len(st.index)} local index entries", flush=True)
    os.makedirs(out_dir, exist_ok=True)
    for fdid in ids:
        try:
            data = st.read_fdid(fdid)
        except Encrypted:
            print(f"ENCRYPTED {fdid}")
            continue
        except KeyError as e:
            print(f"MISSING {fdid} {e.args[0]}")
            continue
        with open(os.path.join(out_dir, str(fdid)), "wb") as f:
            f.write(data)
        print(f"OK {fdid} {len(data)}")


if __name__ == "__main__":
    main()
