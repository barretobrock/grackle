import os
from typing import Tuple
from kavalkilu import Keys
import tempfile
from smb.SMBConnection import SMBConnection


def connect_to_smb() -> Tuple[SMBConnection, str, str]:
    creds = Keys().get_key('gnucash_smb_svc')
    conn = SMBConnection(
        username=creds['un'],
        password=creds['pw'],
        my_name=creds['my_name'],
        remote_name=creds['remote_name'],
        use_ntlm_v2=True
    )
    conn.connect(ip=creds['smb_ip'])

    svc_name = creds['service_name']
    path = creds['filepath']
    return conn, svc_name, path


def get_files(conn: SMBConnection, svc_name: str, source_path: str, dest_path: str):
    files_found = conn.listPath(service_name=svc_name, path=source_path, pattern='*.gnucash')
    if len(files_found) == 0:
        raise ValueError('No matching files found')
    file_found = files_found[0]
    target_path = os.path.join(source_path, file_found.filename)
    with open(dest_path, mode='wb') as file_obj:
        attr, size = conn.retrieveFile(service_name=svc_name, path=target_path, file_obj=file_obj)


if __name__ == '__main__':
    conn, svc, path = connect_to_smb()
    # Copy file
    get_files(conn, svc_name=svc, source_path=path,
              dest_path=os.path.join(tempfile.gettempdir(), 'gnucash_temp.gnucash'))
