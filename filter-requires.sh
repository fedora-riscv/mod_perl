#!/bin/sh

/usr/lib/rpm/perl.req $* |\
    sed -e '/perl(Apache2::FunctionTable)/d' \
        -e '/perl(Apache2::StructureTable)/d' \
        -e '/perl(Apache::TestConfigParse)/d' \
        -e '/perl(Apache::TestConfigPerl)/d' \
	-e '/perl(Data::Flow)/d' \
	-e '/perl(Module::Build)/d' 
