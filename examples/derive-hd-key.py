#!/usr/bin/env python3
#
# Copyright (C) 2018 The python-bitcointx developers
#
# This file is part of python-bitcointx.
#
# It is subject to the license terms in the LICENSE file found in the top-level
# directory of this distribution.
#
# No part of python-bitcointx, including this file, may be copied, modified,
# propagated, or distributed except according to the terms contained in the
# LICENSE file.

import os
import sys
from bitcointx import select_chain_params
from bitcointx.core import b2x
from bitcointx.core.key import BIP32Path
from bitcointx.base58 import Base58Error, UnexpectedBase58PrefixError
from bitcointx.wallet import CCoinExtKey, CCoinExtPubKey
from typing import Union

if __name__ == '__main__':
    xkey: Union[CCoinExtKey, CCoinExtPubKey]

    if len(sys.argv) >= 2 and sys.argv[1] in ('-t', '-r'):
        if sys.argv[1] == '-t':
            select_chain_params('bitcoin/testnet')
        elif sys.argv[1] == '-r':
            select_chain_params('bitcoin/regtest')
        else:
            assert (0)

        sys.argv.pop(1)

    if len(sys.argv) == 2:
        xkey = CCoinExtKey.from_seed(os.urandom(32))
        print("generated xpriv: ", xkey)
    elif len(sys.argv) == 3:
        key_classes = (CCoinExtKey, CCoinExtPubKey)
        for i, cls in enumerate(key_classes):
            try:

                # mypy seems to have problems with tracking the types when
                # iterating over a list of classes.
                # These two lines are essentially the same,
                # but the second one typechecks successfully with mypy 0.701

                # xkey = cls(sys.argv[2])
                xkey = key_classes[i](sys.argv[2])

                break

            except UnexpectedBase58PrefixError:
                pass
            except Base58Error:
                print("ERROR: specified key is incorrectly encoded")
                sys.exit(-1)
            except ValueError:
                pass
        else:
            print("ERROR: specified key does not appear to be valid")
            sys.exit(-1)
    else:
        print("usage: {} [-r|-t] <derivation_path> [xpriv_or_xpub]"
              .format(sys.argv[0]))
        sys.exit(-1)

    path_str = sys.argv[1]

    path = BIP32Path(path_str)

    if len(path) == 0:
        # NOTE: xkey.derive_path() method will raise ValueError
        # on empty path, to guard against bugs:
        #   if there is nothing to derive, why call derive_path() ?
        print('ERROR: nothing to derive, path is empty.')
        sys.exit(-1)

    for n in path:
        print("child number: 0x{:08x}".format(n))
        xkey = xkey.derive(n)
        if isinstance(xkey, CCoinExtKey):
            print("xpriv:", xkey)

            # Note:
            # if xkey is CCoinExtKey, xkey.priv is CCoinKey
            #     CCoinKey is in WIF format, and compressed
            #     len(bytes(xkey.privkey)) == 33
            # if xkey is CExtKey, xkey.priv is CKey
            #     CKey is always 32 bytes
            #
            # Standalone CCoinKey key can be uncompressed,
            # and be of 32 bytes length, but this is not the case
            # with xpriv encapsulated in CCoinExtKey - it is
            # always compressed there.
            #
            # you can always use xkey.priv.secret_bytes
            # to get raw 32-byte secret data from both CCoinKey and CKey
            #
            print("priv WIF:", xkey.priv)
            print("raw priv:", b2x(xkey.priv.secret_bytes))

            print("xpub: ", xkey.neuter())
            print("pub:", b2x(xkey.pub))
        else:
            assert isinstance(xkey, CCoinExtPubKey)
            print("xpub:", xkey)
            print("pub:", b2x(xkey.pub))
