# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import logging

import paramiko

logger = logging.getLogger('common.ssh')


def execute(host, port=22, user="admin", pw="admin", cmd="echo"):
    client = paramiko.SSHClient()
    try:
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, port=port, username=user, password=pw)
        stdin, stdout, stderr = client.exec_command(cmd)
        logger.debug("ssh {}@{}:{} -c {}\nstdin: {}\nstdout: {}\nstderr: {}\n"
                     .format(user, host, port, cmd,
                             stdin,
                             stdout.read() if stdout else None,
                             stderr.read() if stderr else None))
        client.close()
    finally:
        client.close()

    return stdout.read() if stdout else ""
