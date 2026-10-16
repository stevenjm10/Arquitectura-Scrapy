"""Read historical Spanish exports without changing their original files."""

LEGACY_KEYS = {
    'extraido_utc': 'extracted_utc', 'reanudado_utc': 'resumed_utc',
    'perfil': 'profile', 'usuario': 'username', 'cabecera_visible': 'visible_header',
    'biografia': 'bio', 'metodo_biografia': 'bio_method', 'estado_biografia': 'bio_status',
    'seguidores_visible': 'followers_visible', 'seguidores_total': 'followers_total',
    'seguidos_visible': 'following_visible', 'seguidos_total': 'following_total',
    'objetivo_publicaciones': 'post_target', 'limite_por_lista': 'relationship_limit',
    'publicaciones': 'posts', 'seguidores': 'followers', 'seguidos': 'following',
    'descripcion': 'caption', 'fecha': 'date', 'estado': 'status', 'metodo': 'method',
    'estados': 'statuses', 'errores': 'errors', 'enlaces_pendientes': 'pending_links',
    'enlaces_publicaciones': 'post_links', 'resumen': 'summary',
    'con_descripcion': 'with_caption', 'con_fecha': 'with_date',
    'seguidores_recuperados': 'followers_collected', 'seguidos_recuperados': 'following_collected',
}

LEGACY_STATUSES = {
    'objetivo_alcanzado': 'target_reached', 'enlaces_recuperados': 'links_restored',
    'sin_nuevos_enlaces': 'no_new_links', 'integridad_no_verificada': 'completeness_unverified',
    'sin_nuevos_usuarios': 'no_new_users', 'limite_alcanzado': 'limit_reached',
    'muestra_parcial': 'partial_sample', 'en_curso': 'in_progress',
    'resultado_parcial': 'partial_result', 'limite_de_desplazamientos': 'scroll_limit',
    'descripcion_no_detectada': 'caption_not_detected',
    'extraida_revisar_truncamiento': 'extracted_check_truncation',
    'extraida_metadatos_no_verificada': 'metadata_extracted_unverified',
    'vacia_en_metadatos': 'empty_in_metadata', 'no_detectada_automaticamente': 'not_detected_automatically',
    'seleccionada_por_usuario': 'selected_by_user', 'omitida_por_opcion': 'skipped_by_option',
}


def normalize_status(value):
    if not isinstance(value, str):
        return value
    return '; '.join(LEGACY_STATUSES.get(part.strip(), part.strip()) for part in value.split(';'))


def normalize_data(value):
    if isinstance(value, list):
        return [normalize_data(item) for item in value]
    if not isinstance(value, dict):
        return value
    result = {}
    for key, item in value.items():
        name = LEGACY_KEYS.get(key, key)
        converted = normalize_data(item)
        if name in ('status', 'bio_status'):
            converted = normalize_status(converted)
        elif name == 'statuses' and isinstance(converted, dict):
            converted = {field: normalize_status(status) for field, status in converted.items()}
        result[name] = converted
    return result
