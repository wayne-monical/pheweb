'use strict';

function populate_streamtable(phenotypes) {
    $(function() {
        // This is mostly copied from <https://michigangenomics.org/health_data.html>.
        // Preprocess and sort by chrom and pos
        var chromToNum = function(chrom) {
            if (typeof chrom === 'number') return chrom;
            if (!isNaN(chrom)) return Number(chrom);
            if (chrom === 'X') return 24;
            if (chrom === 'Y') return 25;
            return 26; // for other cases
        };
        var data = phenotypes.slice();
        data.sort(function(a, b) {
            var ca = chromToNum(a.chrom);
            var cb = chromToNum(b.chrom);
            if (ca < cb) return -1;
            if (ca > cb) return 1;
            return a.pos - b.pos;
        });
        // data = _.sortBy(data, _.property('pval'));
        var template = _.template($('#streamtable-template').html());
        var view = function(pheno) {
            return template({h: pheno});
        };
        var $found = $('#streamtable-found');
        $found.text(data.length + " phenotypes");

        var callbacks = {
            pagination: function(summary){
                if ($.trim($('#search').val()).length > 0){
                    $found.text(summary.total + " matching phenotypes");
                } else {
                    $found.text(data.length + " phenotypes");
                }
            }
        }

        var options = {
            view: view,
            search_box: '#search',
            callbacks: callbacks,
            pagination: {
                span: 5,
                next_text: 'Next <span class="glyphicon glyphicon-arrow-right" aria-hidden="true"></span>',
                prev_text: '<span class="glyphicon glyphicon-arrow-left" aria-hidden="true"></span> Previous',
                per_page_select: false,
                per_page_opts: [100] // this is the best way I've found to control the number of rows
            },
            // Sort by chrom and pos, even if not displayed in the table
            sort: ['chrom', 'pos']
        }

        $('#stream_table').stream_table(options, data);

    });
}

// Simple stream table: just returns text for each item
function populate_simple_streamtable(items) {
    $(function() {
        var view = function(item) {
            return '<tr>' +
                '<td>' + (item.population || '') + '</td>' +
                '<td>' + (item.chr || '') + '</td>' +
                '<td>' + (item.snp || '') + '</td>' +
                '<td>' + (item.rsid || '') + '</td>' +
                '<td>' + (item.risk_ref || '') + '</td>' +
                '<td>' + (item.locus || '') + '</td>' +
                '<td>' + (item.beta || '') + '</td>' +
                '<td>' + (item.se || '') + '</td>' +
                '<td>' + (item.p || '') + '</td>' +
            '</tr>';
        };
        var options = {
            view: view,
            search_box: '#simple-search',
            pagination: {
                span: 5,
                next_text: 'Next',
                prev_text: 'Previous',
                per_page_select: false,
                per_page_opts: [100]
            }
        };
        // Clear and set table header
        $('#simple_stream_table thead').html('<tr>' +
            '<th>Population</th>' +
            '<th>Chr</th>' +
            '<th>SNP</th>' +
            '<th>RSID</th>' +
            '<th>Risk/Ref</th>' +
            '<th>Locus</th>' +
            '<th>Beta</th>' +
            '<th>SE</th>' +
            '<th>P</th>' +
        '</tr>');
        $('#simple_stream_table').stream_table(options, items);
    });
}
