from crds import rmap, log, utils

def main():
    pmap = rmap.get_cached_mapping("hst.pmap")
    references = pmap.reference_names()
    for ref in references:
        try:
            where = pmap.locate.locate_server_reference(ref)
        except Exception:
            log.error("Can't find", repr(ref))
            continue
        try:
            instr, filekind = utils.get_file_properties(pmap.observatory, where)
        except Exception:
            log.error("Failed get_file_properties() for", repr(ref))

if __name__ == "__main__":
    main()
