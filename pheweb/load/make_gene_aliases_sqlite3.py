
from ..utils import get_gene_tuples_with_ensg, PheWebError
from ..file_utils import get_filepath, get_tmp_path
from .. import conf

import re, json, shutil
from pathlib import Path
import urllib.request
import sqlite3
from typing import List, Dict, Iterable

def get_genenamesorg_ensg_aliases_map(ensgs_to_consider: Iterable[str]) -> Dict[str, List[str]]:
    ensgs_to_consider = set(ensgs_to_consider)
    # r = urllib.request.urlopen('http://ftp.ebi.ac.uk/pub/databases/genenames/new/json/non_alt_loci_set.json')
    r = urllib.request.urlopen('https://storage.googleapis.com/public-download-files/hgnc/json/json/non_alt_loci_set.json')
    data = r.read().decode('utf-8')
    ensg_to_aliases = {}
    for row in json.loads(data)['response']['docs']:
        try:
            if not row.get('ensembl_gene_id',None) or row['ensembl_gene_id'] not in ensgs_to_consider: continue
            assert re.match(r'^ENSG[R0-9\.]+$', row['ensembl_gene_id']), row
            aliases = [row['symbol']] + row.get('prev_symbol',[]) + row.get('alias_symbol',[])
            aliases = [alias for alias in aliases if alias != '']
            aliases = [alias for alias in aliases if re.match(r'^[-\._a-zA-Z0-9]+$', alias)]
            # for alias in aliases: assert re.match(r'^[-\._a-zA-Z0-9]+$', alias), (alias, [ord(c) for c in alias], row)
            ensg_to_aliases[row['ensembl_gene_id']] = aliases
        except Exception:
            raise PheWebError('Cannot handle genenames row: {}'.format(row))
    return ensg_to_aliases

def get_gene_aliases() -> Dict[str, str]:
    # NOTE: "canonical" refers to the canonical symbol for a gene
    genes = [{'canonical': canonical, 'ensg':ensg} for _,_,_,canonical,ensg in get_gene_tuples_with_ensg()]
    assert len({g['ensg'] for g in genes}) == len(genes)
    assert len({g['canonical'] for g in genes}) == len(genes)
    for g in genes:
        assert re.match(r'^ENSGR?[0-9]+(?:\.[0-9]+(?:_[0-9]+)?(?:_PAR_[XY])?)?$', g['ensg']), g
        #assert re.match(r'^[-\._a-zA-Z0-9]+$', g['canonical']), (g['canonical'], [ord(c) for c in g['canonical']], g)
    print('num canonical gene names: {}'.format(len(genes)))

    canonicals_upper = {g['canonical'].upper() for g in genes}
    ensg_to_canonical = {g['ensg']: g['canonical'] for g in genes}
    ensg_to_aliases = get_genenamesorg_ensg_aliases_map(g['ensg'] for g in genes)
    canonical_to_aliases = {ensg_to_canonical[ensg]: ensg_to_aliases.get(ensg, []) for ensg in ensg_to_canonical.keys()}
    for canonical, aliases in canonical_to_aliases.items():
        aliases = [alias for alias in aliases if alias.upper() not in canonicals_upper]
        aliases.append(canonical.upper())
        aliases = list(set(aliases))
        canonical_to_aliases[canonical] = aliases

    alias_to_canonicals:Dict[str,List[str]] = {}
    for canonical, aliases in canonical_to_aliases.items():
        for alias in aliases:
            alias_to_canonicals.setdefault(alias, []).append(canonical)
    return {alias: ','.join(canonicals) for alias,canonicals in alias_to_canonicals.items()}

def download_gene_aliases() -> None:
    aliases_filepath = Path(get_filepath('gene-aliases-sqlite3', must_exist=False))
    aliases_tmp_filepath = Path(get_tmp_path(aliases_filepath))
    print('gene aliases will be stored at {!r}'.format(str(aliases_filepath)))
    if aliases_tmp_filepath.exists(): aliases_tmp_filepath.unlink()
    db = sqlite3.connect(str(aliases_tmp_filepath))
    with db:
        db.execute('CREATE TABLE gene_aliases (alias TEXT PRIMARY KEY, canonicals_comma TEXT)')
        db.executemany('INSERT INTO gene_aliases VALUES (?,?)', sorted(get_gene_aliases().items()))
    aliases_tmp_filepath.replace(aliases_filepath)

def run(argv:List[str]) -> None:
    if '-h' in argv or '--help' in argv:
        print('Make a database of all gene names and their aliases for easy searching.')
        exit(1)

    # This needs genes for filtering
    if not Path(get_filepath('genes', must_exist=False)).exists():
        print('Downloading genes')
        from . import download_genes
        download_genes.run([])

    dest_filepath = Path(get_filepath('gene-aliases-sqlite3', must_exist=False))
    if dest_filepath.exists(): return

    # Check cache_dir
    cache_dir = conf.get_cache_dir()
    if cache_dir:
        cache_filepath = Path(cache_dir) / dest_filepath.name
        if cache_filepath.exists():
            print('Copying {} to {}'.format(cache_filepath, dest_filepath))
            shutil.copy(cache_filepath, dest_filepath)
            return

    if not conf.is_allowed_to_download():
        raise PheWebError("PheWeb is set to disallow downloading files, but couldn't pull {!r} from cache_dir {!r}".format(
            dest_filepath, conf.get_cache_dir()))

    download_gene_aliases()

    if cache_dir:
        print('Cacheing {} at {}'.format(dest_filepath, cache_filepath))
        # It's okay if this doesn't work
        try: shutil.copy(dest_filepath, cache_filepath)
        except Exception: pass

    print('Done')
