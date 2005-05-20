# Makefile for source rpm: mod_perl
# $Id$
NAME := mod_perl
SPECFILE = $(firstword $(wildcard *.spec))
UPSTREAM_CHECKS = asc

include ../common/Makefile.common
