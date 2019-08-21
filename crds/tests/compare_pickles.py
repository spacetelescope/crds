import pickle

import crds
from crds.core import log

def main():
    p = crds.get_cached_mapping("hst.pmap")
    s = pickle.dumps(p)
    q = pickle.loads(s)

    p._trace_compare(q)

    log.divider("p == q --> " + repr(p == q))

    log.divider("__getstate__ --> " + repr(p.__getstate__() == q.__getstate__()))

    log.divider("rmap __getstate__ --> " + repr(p.get_imap("acs").get_rmap("biasfile").__getstate__() == q.get_imap("acs").get_rmap("biasfile").__getstate__()))

if __name__ == "__main__":
    main()
