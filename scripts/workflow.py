"""Versioned local publication: readers see either old or new complete generation.
No network, acquisition, secrets, or deletion of historic records.
"""
from contextlib import contextmanager

import hashlib
import json
import os
from pathlib import Path
import shutil
import uuid
from selected_chat import persist_selected, readable_content, SelectedChatError, archive_identity


def safe_path(path):
    """Reject pre-existing links/reparse points on every ancestor, no race guarantee."""
    path=Path(path).absolute()
    if '..' in path.parts:
        raise SelectedChatError('path traversal rejected')
    for item in (path,*path.parents):
        if item.is_symlink():
            raise SelectedChatError('linked publication path rejected')
        try:
            attributes=getattr(item.lstat(),'st_file_attributes',0)
        except FileNotFoundError:
            continue
        if attributes & 0x400:
            raise SelectedChatError('linked reparse path rejected')
    return path


def sha(path):
    path=safe_path(path)
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()


def atomic_json(path, value):
    path=safe_path(path)
    tmp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    try:
        fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w',encoding='utf-8') as f:
            json.dump(value,f,ensure_ascii=False,indent=2);f.flush();os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if tmp.exists():
            tmp.unlink()  # Only this call's never-published temporary metadata.


@contextmanager
def exclusive(root):
    root=safe_path(root);root.mkdir(parents=True,exist_ok=True,mode=0o700)
    fd=os.open(safe_path(root/'.workflow.lock'),os.O_CREAT|os.O_RDWR,0o600)
    with os.fdopen(fd,'r+b',buffering=0) as lock:
        if os.name=='nt':
            import msvcrt
            if os.fstat(lock.fileno()).st_size==0:lock.write(b'\0')
            lock.seek(0)
        else:
            import fcntl
        try:
            if os.name=='nt':msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
            else:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError as e:
            raise SelectedChatError('another local publication is running') from e
        try:
            yield
        finally:
            if os.name=='nt':
                lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)
            else:fcntl.flock(lock,fcntl.LOCK_UN)


def generation(root, name):
    if not isinstance(name,str) or len(name)!=32 or any(c not in '0123456789abcdef' for c in name):
        raise SelectedChatError('invalid generation ID')
    path=safe_path(Path(root)/'generations'/name)
    if path.is_symlink() or path.parent.is_symlink() or Path(root).is_symlink():
        raise SelectedChatError('linked publication path rejected')
    return path


def current(root):
    root=safe_path(root)
    pointer=root/'current.json'
    if pointer.is_symlink():
        raise SelectedChatError('linked pointer rejected')
    data=json.loads(pointer.read_text(encoding='utf-8'))
    path=generation(root,data['generation'])
    for name,expected in data['hashes'].items():
        if name not in ('archive.sqlite','messages.jsonl','messages.md','manifest.json','run.json'):
            raise SelectedChatError('unexpected publication artifact')
        artifact=path/name
        if artifact.is_symlink() or sha(artifact)!=expected:
            raise SelectedChatError('publication integrity mismatch: '+name)
    if set(data['hashes'])!={'archive.sqlite','messages.jsonl','messages.md','manifest.json','run.json'}:
        raise SelectedChatError('incomplete publication')
    return data,path


def rows(path):
    return [json.loads(line) for line in safe_path(path/'messages.jsonl').read_text(encoding='utf-8').splitlines()]


def semantic(record):
    # Acquisition row location is not a message content change.
    keys=('server_id','local_type','create_time','sender_username','direction','content')
    return {k:record.get(k) for k in keys}


def publish(result, output):
    root=Path(output)
    with exclusive(root):
        previous,old=(current(root) if (root/'current.json').exists() else (None,None))
        name=uuid.uuid4().hex
        target=generation(root,name);target.mkdir(parents=True,mode=0o700)
        if old:
            shutil.copyfile(old/'archive.sqlite',target/'archive.sqlite')
        summary=persist_selected(result,target)
        now=rows(target)
        # Current view follows this capture, not messages missing from this capture.
        # Historic payloads remain in the archive and previous generations.
        from selected_chat import date_window
        begin,finish=date_window(result['manifest']['start'],result['manifest']['end'])
        finish=min(finish,result['manifest']['cutoff_exclusive'])
        before=[r for r in rows(old) if begin<=r['create_time']<finish] if old else []
        source_ids={archive_identity(r,result['manifest']['source_manifest']['account'],result['manifest']['talker']) for r in result['records']}
        now=[r for r in now if r['archive_id'] in source_ids]
        a={r['archive_id']:r for r in before};b={r['archive_id']:r for r in now}
        changes={'added':len(b.keys()-a.keys()),'updated':sum(semantic(b[k])!=semantic(a[k]) for k in b.keys()&a.keys()),
                 'unchanged':sum(semantic(b[k])==semantic(a[k]) for k in b.keys()&a.keys()),'missing':len(a.keys()-b.keys())}
        text=''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in now)
        md='# 指定会话归档\n\n'+'\n\n'.join('## '+r['time']+' · '+r['direction']+' · '+r['archive_id'][:12]+'\n\n'+readable_content(r) for r in now)
        for filename,value in [('messages.jsonl',text),('messages.md',md)]:
            with (target/filename).open('w',encoding='utf-8') as f:
                f.write(value);f.flush();os.fsync(f.fileno())
        report={'generation':name,'previous':previous['generation'] if previous else None,'changes':changes,
                'total':len(now),'archive_total':summary['total'],'inserted':summary['inserted'],
                'start':result['manifest']['start'],'end':result['manifest']['end'],
                'cutoff_exclusive':result['manifest']['cutoff_exclusive'],
                'snapshot_id':result['manifest']['source_manifest'].get('snapshot_id'),
                'snapshot_path':result['manifest'].get('snapshot_path'),
                'missing_interpretation':'not present in current capture; not proof of deletion or recall'}
        atomic_json(target/'run.json',report)
        hashes={n:sha(target/n) for n in ['archive.sqlite','messages.jsonl','messages.md','manifest.json','run.json']}
        atomic_json(root/'current.json',{'schema':'wechat-selected-publication/v1','generation':name,'hashes':hashes})
        return report


def status(root):
    _,path=current(root)
    return json.loads((path/'run.json').read_text(encoding='utf-8'))


def search(root,text=None,start=None,end=None):
    if text is not None and (not isinstance(text,str) or not text):
        raise SelectedChatError('nonempty literal search required')
    _,path=current(root)
    result=rows(path)
    if start is not None or end is not None:
        from selected_chat import date_window
        run=json.loads((path/'run.json').read_text(encoding='utf-8'))
        begin,finish=date_window(start or run['start'],end or run['end'])
        allowed_begin,allowed_finish=date_window(run['start'],run['end'])
        if begin<allowed_begin or finish>allowed_finish:
            raise SelectedChatError('query outside authorized publication dates')
        result=[r for r in result if begin<=r['create_time']<finish]
    return [r for r in result if text is None or text in readable_content(r)]


def history(root):
    data,_=current(root);name=data['generation'];seen=set();reports=[]
    while name is not None:
        if name in seen:
            raise SelectedChatError('history cycle')
        seen.add(name);path=generation(root,name)
        report=json.loads((path/'run.json').read_text(encoding='utf-8'))
        reports.append(report);name=report['previous']
    return reports
