jQuery(document).ready(function ($) {
    setTimeout(function () {
        var sectionID = 'base';
        var search = function ($section, $sidebarItem) {
            $section.children('.section, .function, .method').each(function () {
                if ($(this).hasClass('section')) {
                    sectionID = $(this).attr('id');
                    search($(this), $sidebarItem.parent().find('[href="#'+sectionID+'"]'));
                } else {
                    var $dt = $(this).children('dt');
                    var id = $dt.attr('id');
                    if (id === undefined) {
                        return;
                    }

                    var $functionsUL = $sidebarItem.siblings('[data-sectionID='+sectionID+']');
                    if (!$functionsUL.length) {
                        $functionsUL = $('<ul />').attr('data-sectionID', sectionID);
                        $functionsUL.insertAfter($sidebarItem);
                    }

                    var $li = $('<li />');
                    var $a = $('<a />').css('font-size', '11.5px');
                    var $upperA = $sidebarItem.parent().children('a');
                    var $upperAParent = $upperA.parent();
                    if ($upperAParent.hasClass('toctree-l2')) {
                        $a.css('padding-left', '4em');
                    } else if ($upperAParent.hasClass('toctree-l3')) {
                        if (!$upperA.find('.toctree-expand').length) {
                            $upperA.prepend($('<span />').addClass('toctree-expand'));
                        }
                        $a.css('padding-left', '5em');
                    } else {
                        $a.css('background-color', '#bdbdbd');
                        $a.css('padding-left', '6.25em');
                    }
                    $a.attr('href', '#'+id);
                    $a.text('- '+$dt.find('code').text());
                    $a.click(function () {
                        setTimeout(function () {
                            $a.css('font-weight', 'bold');
                        }, 0);
                    });
                    $li.append($a);
                    $functionsUL.append($li);
                }
            });
        };
        search($('[itemprop=articleBody] > .section'), $('.wy-nav-side a[href="#"]'));
    }, 0);
    $(window).on('hashchange', function () {
        $('ul[data-sectionID]').each(function () {
            $(this).find('a').each(function () {
                $(this).css('font-weight', 'normal');
            });
        });
    });
});
