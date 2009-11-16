{# needs 'node' to be defined #}

    {% ifequal node.class_name 'Page' %}
        {{ node.content_html }}
    {% endifequal %}

    {% ifequal node.class_name 'Image' %}
        <p class="c"><img src="/node/image/{{ node.filename|escape }}" /></p>
        {% if node.caption %}
        <p>{{ node.caption|escape }}</p>
        {% endif %}
        {% if node.credit %}
            {% if node.credit_link %}
        <p>Credit: <a href="{{ node.credit_link|escape }}">{{ node.credit|escape }}</a></p>
            {% else %}
        <p>Credit: {{ node.credit|escape }}</p>
            {% endif %}
        {% endif %}
    {% endifequal %}

    <p class="date">Inserted: {{ node.inserted|date:"Y-m-d H:i" }} ({{ node.inserted|timesince }} ago)</p>
    <p>
        Labels:
    {% for label in node.label %}
        <a href="./label:{{ label|urlencode }}.html">{{ label|escape }}</a>{% if not forloop.last %},{% endif %}
    {% endfor %}
    </p>
