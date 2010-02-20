{# needs 'node' to be defined #}
    <p class="meta" style="float: right;">
      <em>
        Labels:
    {% for label in node.label %}
        <a href="./label:{{ label|urlencode }}.html">{{ label|escape }}</a>{% if not forloop.last %},{% endif %}
    {% endfor %}
      </em>
    </p>
    <p class="meta">
      <em>{{ node.inserted|date:"Y-m-d H:i" }} ({{ node.inserted|timesince }} ago), by <a href="http://www.chilts.org/blog/">chilts</a>.</em>
    </p>

    <div class="entry">

    {% ifequal node.class_name 'Page' %}
        {{ node.content_html }}
    {% endifequal %}

    {% ifequal node.class_name 'Recipe' %}
        {{ node.intro_html }}

        <h2>Ingredients</h2>
        {% if node.serves %}
          <p>
            Serves: {{ node.serves|escape }}
          </p>
        {% endif %}
        {{ node.ingredients_html }}

        <h2>Method</h2>
        {{ node.method_html }}
    {% endifequal %}

    {% ifequal node.class_name 'Image' %}
        <p class="c"><img src="/node/image/{{ node.filename|escape }}" />
        {% if node.caption %}
        <br />
        <strong>{{ node.caption|escape }}</strong>
        {% endif %}
        </p>
        {% if node.credit %}
            {% if node.credit_link %}
        <p>Credit: <a href="{{ node.credit_link|escape }}">{{ node.credit|escape }}</a></p>
            {% else %}
        <p>Credit: {{ node.credit|escape }}</p>
            {% endif %}
        {% endif %}
    {% endifequal %}
    </div>
