PREFIX ?= /usr
DESTDIR ?=
LIBDIR ?= $(PREFIX)/lib
SYSTEM_EXTENSION_DIR ?= $(LIBDIR)/password-store/extensions
MANDIR ?= $(PREFIX)/share/man
BASHCOMPDIR ?= /etc/bash_completion.d

all:
	@echo "pass-meta is a shell script and does not need compilation, it can be simply executed."
	@echo ""
	@echo "To install it try \"make install\" instead."

install:
	@install -v -d "$(DESTDIR)$(MANDIR)/man1"
	@install -v -m 0644 man/pass-extension-meta.1 "$(DESTDIR)$(MANDIR)/man1/pass-meta.1"
	@install -v -d "$(DESTDIR)$(SYSTEM_EXTENSION_DIR)/"
	@install -v -m0755 src/meta.bash "$(DESTDIR)$(SYSTEM_EXTENSION_DIR)/meta.bash"
	@install -v -d "$(DESTDIR)$(BASHCOMPDIR)/"
	@install -v -m 644 completion/pass-meta.bash.completion  "$(DESTDIR)$(BASHCOMPDIR)/pass-meta"
	@echo
	@echo "pass-meta is installed succesfully"
	@echo

uninstall:
	@rm -vrf \
		"$(DESTDIR)$(SYSTEM_EXTENSION_DIR)/meta.bash" \
		"$(DESTDIR)$(MANDIR)/man1/pass-meta.1" \
		"$(DESTDIR)$(BASHCOMPDIR)/pass-meta"

lint:
	shellcheck -s bash src/meta.bash

.PHONY: install uninstall lint
