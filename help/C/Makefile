pages=$(wildcard *.page)
htmls=$(patsubst %.page,%.html,$(pages))

all: $(htmls) index.cache

index.cache : $(pages)
	echo '<cache xmlns="http://projectmallard.org/1.0/">' > $@.in
	for page in $(pages); do \
	  echo "<page href='$$page'/>" >> $@.in; \
	done
	echo '</cache>' >> $@.in
	xsltproc `pkg-config --variable xsltdir gnome-doc-utils`/mallard/utils/mal2cache.xsl $@.in | xmllint --format - > $@
	rm $@.in

$(htmls) : index.cache
$(htmls) : %.html : %.page
	xsltproc \
	  --stringparam mal.cache.file `pwd`/index.cache \
	  --param mal.chunk.chunk_top 1 \
	  `pkg-config --variable mal2html gnome-doc-utils` $<

.PHONY: clean
clean:
	rm index.cache *.html
