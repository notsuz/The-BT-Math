(function () {
  function whenReady(fn) {
    var $ = window.django && window.django.jQuery;
    if (!$) return; // select2/Jazzmin require jQuery; nothing to wire without it
    $(fn);
  }

  // Jazzmin applies select2 to every <select> on the page (see its
  // change_form.js), which wraps the real element in its own dropdown UI
  // that caches the option list at init time. Rebuilding childField's
  // <option>s below doesn't touch that cached UI, so select2 has to be
  // explicitly destroyed and re-initialized to pick the new options up.
  function refreshSelect2($, el) {
    if (!$.fn.select2) return;
    var $el = $(el);
    if ($el.hasClass("select2-hidden-accessible")) {
      $el.select2("destroy");
    }
    $el.select2({ width: "100%" });
  }

  // Filters `childField`'s options down to whichever value is selected in
  // `parentField`, matching on each <option>'s data-{dataAttr} attribute.
  // Bound and triggered through jQuery throughout - select2 raises its
  // selection-changed event via `$el.trigger('change')`, which a plain
  // `addEventListener('change', ...)` never sees.
  function wireCascade($, parentField, childField, dataAttr) {
    var allOptions = Array.prototype.slice.call(childField.options);
    var lastParentValue = parentField.value;

    function refresh(preserveSelection) {
      var parentId = parentField.value;
      var previousValue = preserveSelection ? childField.value : "";

      childField.innerHTML = "";
      allOptions.forEach(function (opt) {
        var optParent = opt.getAttribute("data-" + dataAttr);
        if (!opt.value || !parentId || optParent === parentId) {
          childField.appendChild(opt.cloneNode(true));
        }
      });

      var stillValid = Array.prototype.some.call(childField.options, function (o) {
        return o.value === previousValue;
      });
      childField.value = stillValid ? previousValue : "";
      refreshSelect2($, childField);
      $(childField).trigger("change");
    }

    // Guard against no-op "change" events: Jazzmin (and this same cascade,
    // via the trigger above) re-fires "change" on filter/select fields
    // during setup just to sync internal state, without the value actually
    // changing. Only a genuine value change should reset the child field.
    $(parentField).on("change", function () {
      if (parentField.value === lastParentValue) return;
      lastParentValue = parentField.value;
      refresh(false);
    });

    return refresh;
  }

  whenReady(function () {
    var $ = window.django.jQuery;
    var categoryField = document.getElementById("id_category");
    var programField = document.getElementById("id_program");
    var courseField = document.getElementById("id_course");
    if (!categoryField || !programField || !courseField) return;

    var chaptersDataEl = document.getElementById("chapters-by-course-data");
    var chaptersByCourse = chaptersDataEl ? JSON.parse(chaptersDataEl.textContent) : {};

    // Anchored to the whole field row (not the <select> itself) because
    // select2 inserts its own widget as courseField's next sibling - putting
    // the preview there directly would race with select2 over who ends up
    // visually on top.
    var preview = document.createElement("div");
    preview.id = "chapter-course-preview";
    var courseFieldRow = courseField.closest(".form-row, .field-box") || courseField.parentElement;
    courseFieldRow.appendChild(preview);

    function renderChaptersPreview() {
      var chapters = chaptersByCourse[courseField.value];
      if (!chapters || !chapters.length) {
        preview.innerHTML = courseField.value ? "<em>No chapters yet in this course.</em>" : "";
        return;
      }
      var items = chapters
        .map(function (ch) {
          return "<li>" + ch.order + ". " + ch.title + (ch.is_free ? " (Free)" : "") + "</li>";
        })
        .join("");
      preview.innerHTML = "<strong>Existing chapters in this course:</strong><ul>" + items + "</ul>";
    }

    // Change on courseField fires both from direct user selection and from
    // the program->course cascade above (refresh() triggers "change" too).
    $(courseField).on("change", renderChaptersPreview);

    var refreshPrograms = wireCascade($, categoryField, programField, "category");
    var refreshCourses = wireCascade($, programField, courseField, "program");

    // Initial load: narrow each level from whatever was pre-filled
    // server-side (edit mode), preserving the existing selections.
    refreshPrograms(true);
    refreshCourses(true);
    renderChaptersPreview();
  });
})();
