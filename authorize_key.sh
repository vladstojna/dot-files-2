#!/usr/bin/env bash

if grep -q "$VAGRANT_PUBKEY" "$HOME/.ssh/authorized_keys"; then
    echo "Key already exists"
else
    cat $VAGRANT_PUBKEY >> $HOME/.ssh/authorized_keys
fi
rm -f $VAGRANT_PUBKEY
