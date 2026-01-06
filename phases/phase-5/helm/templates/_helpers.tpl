{{- define "evo-todo.name" -}}
{{- .Chart.Name -}}
{{- end -}}

{{- define "evo-todo.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
