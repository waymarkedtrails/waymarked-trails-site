all:
	@echo "Available targets:"
	@echo "  trans-extract: extract new translations"
	@echo "  trans-compile: compile all translations"

trans-extract:
	pybabel-python3 extract -o django/locale/qot/LC_MESSAGES/django.po --project='Waymarked Trails Map' --copyright-holder='Sarah Hoffmann' --sort-output --no-wrap --msgid-bugs-address=lonvia@denofr.de -F config/i18n.cfg .

POFILES=$(shell echo django/locale/*/LC_MESSAGES/django.po)
MOFILES=$(subst .po,.mo, $(POFILES))

%.mo : %.po
	msgfmt -o $@ $<

trans-compile: $(MOFILES)
