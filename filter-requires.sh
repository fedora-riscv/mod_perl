#!/bin/sh

/usr/lib/rpm/perl.req $* |\
    sed -e '/perl(Apache::FunctionTable)/d' \
        -e '/perl(Apache::StructureTable)/d' \
        -e '/perl(Apache::TestConfigParse)/d' \
        -e '/perl(Apache::TestConfigPerl)/d'
