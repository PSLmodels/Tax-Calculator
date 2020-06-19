// base.js v1.0


// Declare MathJax Macros for the Appropriate Macros
MathJax.Hub.Config({
    TeX: {
      Macros: {
        Var:     "\\mathop{\\mathrm{Var}}",
        trace:   "\\mathop{\\mathrm{trace}}",
        argmax:  "\\mathop{\\mathrm{arg\\,max}}",
        argmin:  "\\mathop{\\mathrm{arg\\,min}}",
        proj:  "\\mathop{\\mathrm{proj}}",
        col:  "\\mathop{\\mathrm{col}}",
        Span:  "\\mathop{\\mathrm{span}}",
        epsilon: "\\varepsilon",
        EE: "\\mathbb{E}",
        PP: "\\mathbb{P}",
        RR: "\\mathbb{R}",
        NN: "\\mathbb{N}",
        ZZ: "\\mathbb{Z}",
        aA: "\\mathcal{A}",
        bB: "\\mathcal{B}",
        cC: "\\mathcal{C}",
        dD: "\\mathcal{D}",
        eE: "\\mathcal{E}",
        fF: "\\mathcal{F}",
        gG: "\\mathcal{G}",
        hH: "\\mathcal{H}",
      }
    }
  });
  MathJax.Hub.Config({
    tex2jax: {
      inlineMath: [ ['$','$'], ['\\(','\\)'] ],
      processEscapes: true
    }
  });
  
  
  /* Collapsed code block */
  
  const collapsableCodeBlocks = document.querySelectorAll("div[class^='collapse'] .highlight");
  for (var i = 0; i < collapsableCodeBlocks.length; i++) {
    const toggleContainer = document.createElement('div');
    toggleContainer.innerHTML = '<a href="#" class="toggle toggle-less" style="display:none;"><span class="icon icon-angle-double-up"></span><em>Show less...</em></a><a href="#" class="toggle toggle-more"><span class="icon icon-angle-double-down"></span><em>Show more...</em></a>';
    collapsableCodeBlocks[i].parentNode.insertBefore(toggleContainer, collapsableCodeBlocks[i].nextSibling);
  }
  
  const collapsableCodeToggles = document.querySelectorAll("div[class^='collapse'] .toggle");
  for (var i = 0; i < collapsableCodeToggles.length; i++) {
    collapsableCodeToggles[i].addEventListener('click', function(e) {
      e.preventDefault();
      var codeBlock = this.closest('div[class^="collapse"]');
      if ( codeBlock.classList.contains('expanded') ) {
        codeBlock.classList.remove('expanded');
        this.style.display = 'none';
        this.nextSibling.style.display = 'block';  
      } else {
        codeBlock.classList.add('expanded');
        this.style.display = 'none';
        this.previousSibling.style.display = 'block';
      }
    });
  }
  
  
  /* Wrap container around all tables allowing hirizontal scroll */
  
  const contentTables = document.querySelectorAll(".content table");
  for (var i = 0; i < contentTables.length; i++) {
    var wrapper = document.createElement('div');
    wrapper.classList.add('table-container');
    contentTables[i].parentNode.insertBefore(wrapper, contentTables[i]);
    wrapper.appendChild(contentTables[i]);
  }
  
  
  // Populate status page from code execution results JSON
  
  function loadCodeExecutionJSON(callback) {   
    var xobj = new XMLHttpRequest();
        xobj.overrideMimeType("application/json");
    xobj.open('GET', '_static/code-execution-results.json', true); // Replace 'appDataServices' with the path to your file
    xobj.onreadystatechange = function () {
          if (xobj.readyState == 4 && xobj.status == "200") {
            // Required use of an anonymous callback as .open will NOT return a value but simply returns undefined in asynchronous mode
            callback(xobj.responseText);
          }
    };
    xobj.send(null);  
  }
  
  if ( document.getElementById('status_table') ) {
  
    loadCodeExecutionJSON(function(response) {
      // Parsing JSON string into object
      var data = JSON.parse(response);
      var status_data = [];
      var last_test_time = data.run_time;
      document.getElementById('last_test_time').textContent = last_test_time;
      for (var key in data.results)
      {
          var new_record = {};
          new_record['name'] = data.results[key].filename;
          new_record['runtime'] = data.results[key].runtime;
          new_record['extension'] = data.results[key].extension;
          new_record['result'] = data.results[key].num_errors;
          new_record['language'] = data.results[key].language;
  
          status_data.push(new_record);
      }
  
      // empty the table
      var table = document.getElementById("status_table");
      while (table.firstChild)
        table.removeChild(table.firstChild);
        var rawHTML = "<tr><th class='resultsTableHeader'>Lecture File</th><th class='resultsTableHeader'>Language</th><th>Running Time</th><th></th></tr>";
        table.innerHTML = rawHTML;
      // add the data
      for (var i = 0; i < status_data.length; i ++)
      {
        var table = document.getElementById("status_table");
        var row = table.insertRow(-1);
        row.setAttribute("id", status_data[i]['name'], 0);
  
        // Insert new cells (<td> elements) at the 1st and 2nd position of the "new" <tr> element:
        var lectureCell = row.insertCell(0);
        var langCell = row.insertCell(1);
        var runtimeCell = row.insertCell(2);
        var statusCell = row.insertCell(3);
        var badge, status, color, lang, link;
  
        if (status_data[i]['result'] === 0)
        {
            status = "Passing";
            color = "brightgreen";
        }
        else if (status_data[i]['result'] === 1)
        {
            status = "Failing";
            color = "red";
        }
        else if (status_data[i]['result'] === -1) {
            status = "Not available";
            color = "lightgrey";
        }
  
        link = '/' + status_data[i]['name'] + '.html';
  
        badge = '<a href="' + link + '"><img src="https://img.shields.io/badge/Execution%20test-' + status + '-' + color + '.svg"></a>';
  
        // Add some text to the new cells:
        lectureCell.innerHTML = status_data[i]['name'];
        langCell.innerHTML = status_data[i]['language'];
        runtimeCell.innerHTML = status_data[i]['runtime'];
        statusCell.innerHTML = badge;
  
  
      }
    })
  }
  
  
  // Show executability status badge in header
  
  const LECTURE_OK = 0;
  const LECTURE_FAILED = 1;
  const LECTURE_ERROR = -1;
  
  function update_page_badge(page_status)
  {
      var badge = document.getElementById("executability_status_badge");
      var status, color;
  
      if (page_status === LECTURE_OK)
      {
          status = "Passing";
          color = "brightgreen";
      }
      else if (page_status == LECTURE_FAILED)
      {
          status = "Failing";
          color = "red";
      }
      else if (page_status == LECTURE_ERROR)
      {
          status = "Not available";
          color = "lightgrey";
      }
      else
      {
          console.log("Panic! Invalid parameter passed to update_page_badge().");
      }
  
      badge.innerHTML = '<a href="/status.html"><img src="https://img.shields.io/badge/Execution%20test-' + status + '-' + color + '.svg"></a>';
  
      //badge.style.display="block";
  
      return;
  }
  
  function determine_page_status(status_data)
  {
      var path = window.location.pathname;
      var filename_parts = path.split("/");
      var filename = filename_parts.pop();
  
      var lecture_name = filename.split(".")[0].toLowerCase();
  
      var res = LECTURE_ERROR;
  
      for (var i = 0; i < status_data.length; i ++)
      {
          if (status_data[i]['name'].split('/').pop() === lecture_name)
          {
              if (status_data[i]['result'] === 0)
              {
                  res = LECTURE_OK;
              }
              else
              {
                  res = LECTURE_FAILED;
              }
          }
      }
      return res;
  }
  
  function load_this_page_badge()
  {
    loadCodeExecutionJSON(function(response) {
      // Parsing JSON string into object
      var data = JSON.parse(response);
      status_data = [];
      for (var key in data.results)
      {
          var new_record = {};
          new_record['name'] = data.results[key].filename;
          new_record['runtime'] = data.results[key].runtime;
          new_record['extension'] = data.results[key].extension;
          new_record['result'] = data.results[key].num_errors;
          new_record['language'] = data.results[key].language;
          status_data.push(new_record);
      }
      var page_status = determine_page_status(status_data);
      update_page_badge(page_status);
    });
  }
  
  function get_badge(percentage)
  {
      var color, badge;
  
      if (percentage > -1)
      {
        if ( percentage < 50 ) {
          color = 'red';
        } else {
          color = 'brightgreen';
        }
        badge = 'https://img.shields.io/badge/Total%20coverage-' + percentage + '%25-' + color + '.svg';
      } else {
        badge = 'https://img.shields.io/badge/Total%20coverage-not%20available-lightgrey.svg>';
      }
      return badge;
  }
  
  function load_percentages()
  {
    var number_of_lectures = {};
    var number_which_passed = {};
    var keys_list = [];
    var combined_percentage;
  
    loadCodeExecutionJSON(function(response) {
      // Parsing JSON string into object
      var data = JSON.parse(response);
      for (var key in data.results)
      {
        if (data.results[key].num_errors === 0)
        {
          if (!(data.results[key].extension in number_which_passed))
          {
              number_which_passed[data.results[key].extension] = 0;
              keys_list.push(data.results[key].extension);
          }
          number_which_passed[data.results[key].extension] += 1;
        }
  
        if (!(data.results[key].extension in number_of_lectures))
        {
          number_of_lectures[data.results[key].extension] = 0;
        }
        number_of_lectures[data.results[key].extension] += 1;
      }
  
      var percentages = {};
      var total_lectures = 0;
      var total_passing = 0;
      for (var k in keys_list)
      {
          key = keys_list[k];
  
          percentages[key] = 0;
          if (number_of_lectures[key] === 0)
          {
              // An appropriate value for this is yet to be determined.
              percentages[key] = 100;
          }
          else
          {
              percentages[key] = Math.floor(100 * number_which_passed[key] / number_of_lectures[key]);
          }
  
          // Sensible boundary checking.
          if (percentages[key] < 0 || percentages[key] > 100)
          {
              percentages[key] = -1;
          }
  
          total_lectures += number_of_lectures[key];
          total_passing += number_which_passed[key];
      }
  
      if (total_lectures === 0)
      {
          combined_percentage = 0;
      }
      else
      {
          combined_percentage = Math.floor(100 * total_passing / total_lectures);
      }
  
      var badge = document.getElementById("coverage_badge");
      badge.innerHTML = '<a href="/status.html"><img src="' + get_badge(combined_percentage) + '"></a>';
  
    });
  
  }
  
  if ( document.getElementById('executability_status_badge') ) {
    load_this_page_badge();
  }
  
  if ( document.getElementById('coverage_badge') ) {
    load_percentages();
  }