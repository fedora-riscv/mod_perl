# Makefile for source rpm: mod_perl
# $Id$
NAME := mod_perl
SPECFILE = $(firstword $(wildcard *.spec))

include ../common/Makefile.common
