-- a) Solicitudes por categoría y por área (categoría = etiqueta de origen, la IA se mide aparte)
SELECT s.etiqueta_esperada AS categoria, COALESCE(e.area, 'Empleado inexistente') AS area, COUNT(*) AS total
FROM solicitudes s LEFT JOIN empleados e ON e.id_empleado = s.id_empleado
GROUP BY categoria, area ORDER BY categoria, area;

-- b) Solicitudes de empleados que no existen en la nómina
SELECT s.id_solicitud, s.id_empleado, s.texto
FROM solicitudes s LEFT JOIN empleados e ON e.id_empleado = s.id_empleado
WHERE e.id_empleado IS NULL;

-- c) Empleados con menos de 5 días de vacaciones disponibles
SELECT id_empleado, nombre, area, dias_vacaciones
FROM empleados WHERE dias_vacaciones < 5 ORDER BY dias_vacaciones;
