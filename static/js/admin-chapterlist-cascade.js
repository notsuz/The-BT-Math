(function () {
  function whenReady(fn) {
    var $ = window.django && window.django.jQuery;
    if (!$) return; // select2/Jazzmin require jQuery; nothing to wire without it
    $(fn);
  }

  function readJSON(id) {
    var el = document.getElementById(id);
    return el ? JSON.parse(el.textContent) : {};
  }

  // Same select2 workaround as admin-chapter-cascade.js: Jazzmin's own
  // change_list.js turns every ".search-filter" <select> into a select2
  // widget on load, which caches the option list at init time. Rebuilding
  // childSelect's <option>s below doesn't touch that cached UI, so select2
  // has to be explicitly destroyed and re-initialized to pick the new
  // options up.
  function refreshSelect2($, el) {
    if (!$.fn.select2) return;
    var $el = $(el);
    if ($el.hasClass("select2-hidden-accessible")) {
      $el.select2("destroy");
    }
    $el.select2({ width: "100%" });
  }

  function findFilterSelect(dataName) {
    return document.querySelector('select.search-filter[data-name="' + dataName + '"]');
  }

  // Filters `childSelect`'s options down to whichever value is selected in
  // `parentSelect`, using `allowedIdsFor(parentId)` to look up the allowed
  // child ids. Bound and triggered through jQuery throughout - select2
  // raises its selection-changed event via `$el.trigger('change')`, which a
  // plain `addEventListener('change', ...)` never sees (this was the actual
  // bug: the filters looked wired up but never actually narrowed anything).
  function wireCascade($, parentSelect, childSelect, allowedIdsFor) {
    var allOptions = Array.prototype.slice.call(childSelect.options);
    var lastParentValue = parentSelect.value;

    function refresh(preserveSelection) {
      var parentId = parentSelect.value;
      var previousValue = preserveSelection ? childSelect.value : "";
      var allowed = parentId ? allowedIdsFor(parentId) : null;

      childSelect.innerHTML = "";
      allOptions.forEach(function (opt) {
        if (!opt.value || !allowed || allowed.indexOf(opt.value) !== -1) {
          childSelect.appendChild(opt.cloneNode(true));
        }
      });

      var stillValid = Array.prototype.some.call(childSelect.options, function (o) {
        return o.value === previousValue;
      });
      childSelect.value = stillValid ? previousValue : "";
      refreshSelect2($, childSelect);
      $(childSelect).trigger("change");
    }

    // Guard against no-op "change" events: Jazzmin's own search_filters()
    // triggers "change" on every filter select during setup just to sync
    // the select's `name` attribute, without the value actually changing.
    // Only a genuine value change should reset/narrow the child select.
    $(parentSelect).on("change", function () {
      if (parentSelect.value === lastParentValue) return;
      lastParentValue = parentSelect.value;
      refresh(false);
    });

    return refresh;
  }

  whenReady(function () {
    var $ = window.django.jQuery;
    var categorySelect = findFilterSelect("course__program__category");
    var programSelect = findFilterSelect("course__program");
    var courseSelect = findFilterSelect("course");
    if (!categorySelect || !programSelect || !courseSelect) return;

    var categoryToPrograms = readJSON("chapter-category-to-programs");
    var programToCourses = readJSON("chapter-program-to-courses");

    function allowedIds(map, parentId) {
      return (map[parentId] || []).map(String);
    }

    var refreshPrograms = wireCascade($, categorySelect, programSelect, function (categoryId) {
      return allowedIds(categoryToPrograms, categoryId);
    });
    var refreshCourses = wireCascade($, programSelect, courseSelect, function (programId) {
      return allowedIds(programToCourses, programId);
    });

    // Initial load: narrow each level from whatever is pre-selected (e.g.
    // after clicking Search with a category filter applied), preserving
    // the existing selections.
    refreshPrograms(true);
    refreshCourses(true);
  });
})();
