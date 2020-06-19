{%- extends 'display_priority.tpl' -%}

{% set site_title = 'Documentation' %}
{% set nb_title = nb.metadata.get('title', '') %}
{% set nb_filename = nb.metadata.get('filename', '') %}
{% set nb_filename_with_path = nb.metadata.get('filename_with_path','') %}
{% set indexPage = nb_filename.startswith('index') %}
{% set download_nb = nb.metadata.get('download_nb','') %}
{% set download_nb_path = nb.metadata.get('download_nb_path','') %}
{% if nb_filename.endswith('.rst') %}
{% set nb_filename = nb_filename[:-4] %}
{% endif %}

{%- block header %}
<!doctype html>
<html lang="en">
	<head>
		<meta charset="utf-8">
{% if nb_filename == 'index' %}
		<title>{{ site_title }}</title>
{% else %}
		<title>{{nb_title}} &ndash; {{ site_title }}</title>
{% endif %}
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<meta name="author" content="">
		<meta name="keywords" content="">
		<meta name="description" content="">

		<link rel="stylesheet" href="/_static/css/base.css">

	</head>

	<body>

		<div class="wrapper">

			<header class="header">

				<div class="branding">

					<p class="site-title"><a href="/">{{ site_title }}</a></p>

					<p class="sr-only"><a href="#skip">Skip to content</a></p>

				</div>

				<div class="header-tools">

{% if indexPage or nb_filename == 'status' %}
					<div class="header-badge" id="coverage_badge"></div>
{% else %}
					<div class="header-badge" id="executability_status_badge"></div>
{% endif %}

				</div>

			</header>

			<div class="main">

				<div class="content">

					<div id="skip"></div>

					<div class="document">

{%- endblock header-%}

{% block codecell %}
{% set html_class = cell['metadata'].get('html-class', {}) %}
<div class="{{ html_class }} cell border-box-sizing code_cell rendered">
{{ super() }}
</div>
{%- endblock codecell %}

{% block input_group -%}
<div class="input">
{{ super() }}
</div>
{% endblock input_group %}

{% block output_group %}
<div class="output_wrapper">
<div class="output">
{{ super() }}
</div>
</div>
{% endblock output_group %}

{% block in_prompt -%}
<div class="prompt input_prompt">
	{%- if cell.execution_count is defined -%}
		In&nbsp;[{{ cell.execution_count|replace(None, "&nbsp;") }}]:
	{%- else -%}
		In&nbsp;[&nbsp;]:
	{%- endif -%}
</div>
{%- endblock in_prompt %}

{% block empty_in_prompt -%}
<div class="prompt input_prompt">
</div>
{%- endblock empty_in_prompt %}

{# 
  output_prompt doesn't do anything in HTML,
  because there is a prompt div in each output area (see output block)
#}
{% block output_prompt %}
{% endblock output_prompt %}

{% block input %}
<div class="inner_cell">
	<div class="input_area">
{{ cell.source | highlight_code(metadata=cell.metadata) }}
	</div>
</div>
{%- endblock input %}

{% block output_area_prompt %}
{%- if output.output_type == 'execute_result' -%}
	<div class="prompt output_prompt">
	{%- if cell.execution_count is defined -%}
		Out[{{ cell.execution_count|replace(None, "&nbsp;") }}]:
	{%- else -%}
		Out[&nbsp;]:
	{%- endif -%}
{%- else -%}
	<div class="prompt">
{%- endif -%}
	</div>
{% endblock output_area_prompt %}

{% block output %}
<div class="output_area">
{% if resources.global_content_filter.include_output_prompt %}
	{{ self.output_area_prompt() }}
{% endif %}
{{ super() }}
</div>
{% endblock output %}

{% block markdowncell scoped %}
{% set html_class = cell['metadata'].get('html-class', {}) %}
<div class="{{ html_class }} cell border-box-sizing text_cell rendered">
{%- if resources.global_content_filter.include_input_prompt-%}
	{{ self.empty_in_prompt() }}
{%- endif -%}
<div class="inner_cell">
<div class="text_cell_render border-box-sizing rendered_html">
{{ cell.source  | markdown2html | strip_files_prefix }}
</div>
</div>
</div>
{%- endblock markdowncell %}

{% block unknowncell scoped %}
unknown type  {{ cell.type }}
{% endblock unknowncell %}

{% block execute_result -%}
{%- set extra_class="output_execute_result" -%}
{% block data_priority scoped %}
{{ super() }}
{% endblock data_priority %}
{%- set extra_class="" -%}
{%- endblock execute_result %}

{% block stream_stdout -%}
<div class="output_subarea output_stream output_stdout output_text">
<pre>
{{- output.text | ansi2html -}}
</pre>
</div>
{%- endblock stream_stdout %}

{% block stream_stderr -%}
<div class="output_subarea output_stream output_stderr output_text">
<pre>
{{- output.text | ansi2html -}}
</pre>
</div>
{%- endblock stream_stderr %}

{% block data_svg scoped -%}
<div class="output_svg output_subarea {{ extra_class }}">
{%- if output.svg_filename %}
<img src="{{ output.svg_filename | posix_path }}"
{%- else %}
{{ output.data['image/svg+xml'] }}
{%- endif %}
</div>
{%- endblock data_svg %}

{% block data_html scoped -%}
<div class="output_html rendered_html output_subarea {{ extra_class }}">
{{ output.data['text/html'] }}
</div>
{%- endblock data_html %}

{% block data_markdown scoped -%}
<div class="output_markdown rendered_html output_subarea {{ extra_class }}">
{{ output.data['text/markdown'] | markdown2html }}
</div>
{%- endblock data_markdown %}

{% block data_png scoped %}
<div class="output_png output_subarea {{ extra_class }}">
{%- if 'image/png' in output.metadata.get('filenames', {}) %}
<img src="{{ output.metadata.filenames['image/png'] | posix_path }}"
{%- else %}
<img src="data:image/png;base64,{{ output.data['image/png'] }}"
{%- endif %}
{%- set width=output | get_metadata('width', 'image/png') -%}
{%- if width is not none %}
width={{ width }}
{%- endif %}
{%- set height=output | get_metadata('height', 'image/png') -%}
{%- if height is not none %}
height={{ height }}
{%- endif %}
{%- if output | get_metadata('unconfined', 'image/png') %}
class="unconfined"
{%- endif %}
>
</div>
{%- endblock data_png %}

{% block data_jpg scoped %}
<div class="output_jpeg output_subarea {{ extra_class }}">
{%- if 'image/jpeg' in output.metadata.get('filenames', {}) %}
<img src="{{ output.metadata.filenames['image/jpeg'] | posix_path }}"
{%- else %}
<img src="data:image/jpeg;base64,{{ output.data['image/jpeg'] }}"
{%- endif %}
{%- set width=output | get_metadata('width', 'image/jpeg') -%}
{%- if width is not none %}
width={{ width }}
{%- endif %}
{%- set height=output | get_metadata('height', 'image/jpeg') -%}
{%- if height is not none %}
height={{ height }}
{%- endif %}
{%- if output | get_metadata('unconfined', 'image/jpeg') %}
class="unconfined"
{%- endif %}
>
</div>
{%- endblock data_jpg %}

{% block data_latex scoped %}
<div class="output_latex output_subarea {{ extra_class }}">
{{ output.data['text/latex'] }}
</div>
{%- endblock data_latex %}

{% block error -%}
<div class="output_subarea output_text output_error">
<pre>
{{- super() -}}
</pre>
</div>
{%- endblock error %}

{%- block traceback_line %}
{{ line | ansi2html }}
{%- endblock traceback_line %}

{%- block data_text scoped %}
<div class="output_text output_subarea {{ extra_class }}">
<pre>
{{- output.data['text/plain'] | ansi2html -}}
</pre>
</div>
{%- endblock -%}

{%- block data_javascript scoped %}
{% set div_id = uuid4() %}
<div id="{{ div_id }}"></div>
<div class="output_subarea output_javascript {{ extra_class }}">
<script type="text/javascript">
var element = $('#{{ div_id }}');
{{ output.data['application/javascript'] }}
</script>
</div>
{%- endblock -%}

{%- block data_widget_state scoped %}
{% set div_id = uuid4() %}
{% set datatype_list = output.data | filter_data_type %} 
{% set datatype = datatype_list[0]%} 
<div id="{{ div_id }}"></div>
<div class="output_subarea output_widget_state {{ extra_class }}">
<script type="text/javascript">
var element = $('#{{ div_id }}');
</script>
<script type="{{ datatype }}">
{{ output.data[datatype] | json_dumps }}
</script>
</div>
{%- endblock data_widget_state -%}

{%- block data_widget_view scoped %}
{% set div_id = uuid4() %}
{% set datatype_list = output.data | filter_data_type %} 
{% set datatype = datatype_list[0]%} 
<div id="{{ div_id }}"></div>
<div class="output_subarea output_widget_view {{ extra_class }}">
<script type="text/javascript">
var element = $('#{{ div_id }}');
</script>
<script type="{{ datatype }}">
{{ output.data[datatype] | json_dumps }}
</script>
</div>
{%- endblock data_widget_view -%}

{%- block footer %}
{% set mimetype = 'application/vnd.jupyter.widget-state+json'%} 
{% if mimetype in nb.metadata.get("widgets",{})%}
<script type="{{ mimetype }}">
{{ nb.metadata.widgets[mimetype] | json_dumps }}
</script>
{% endif %}
{{ super() }}


					</div>

				</div>

			</div>

			<footer class="footer">

				<p>&copy; Copyright <YEAR>, Built using the minimal jupinx template.</p>

			</footer>

		</div>

		<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>
		<script src="/_static/js/base.js"></script>

	</body>
</html>


{%- endblock footer-%}
