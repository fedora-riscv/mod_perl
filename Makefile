# Makefile for source rpm: mod_perl
# $Id: Makefile,v 1.1 2004/09/09 08:39:40 cvsdist Exp $
NAME := mod_perl
SPECFILE = $(firstword $(wildcard *.spec))
UPSTREAM_CHECKS = asc

include ../common/Makefile.common
