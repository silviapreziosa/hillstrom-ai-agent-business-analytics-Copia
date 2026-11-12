# Instrument controls — enumerated fixtures

Note: deduplicated counts are counts of distinct rows, which may undercount distinct customers when rows are indistinguishable.

Lessons pinned by V-0A/V-0B:
- V-0A: an identifier column does NOT remove exact duplicates when the copies inherit the source record's ID (duplicates remain 2).
- V-0B: identical characteristics with DIFFERENT customer IDs are not detected by row-deduplication: it counts rows, never customers.

Both recomputation paths were authored by the analysis agent; agreement between them rules out coding slips but is not an independent audit.
