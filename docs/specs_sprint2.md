# Especificaciones de Comportamiento - Sprint 2
## PetCare Connect - Gestión de Productos/Servicios

## HU-01: Registro de Producto/Servicio (Ofertante)

**Como** Ofertante (cuidador) **Quiero** registrar un nuevo servicio **Para** que pueda ser ofertado en la plataforma

### Especificación 1: Registro exitoso - estado pendiente

```gherkin
Scenario: Registro exitoso de un servicio
  Given estoy autenticado como cuidador
  And tengo los siguientes datos del servicio:
    | Campo       | Valor                    |
    | titulo      | Paseo de mascotas        |
    | descripcion | Paseo de 30 minutos      |
    | precio      | 50.00                    |
    | categoria   | paseo                    |
  When envío la solicitud POST /api/productos
  Then el sistema debe crear el servicio
  And el estado del servicio debe ser "pendiente"
  And el servicio no debe ser visible para demandantes
  And el código de respuesta debe ser 201
```

### Especificación 2: Registro con datos incompletos

```gherkin
Scenario: Intento de registro con datos incompletos
  Given estoy autenticado como cuidador
  When envío la solicitud POST /api/productos sin el campo "titulo"
  Then el sistema debe retornar error 400
  And el mensaje debe indicar "El campo titulo es requerido"
  And el servicio no debe ser creado
```

### Especificación 3: Registro con precio inválido

```gherkin
Scenario: Intento de registro con precio negativo
  Given estoy autenticado como cuidador
  And tengo un precio de -10.00
  When envío la solicitud POST /api/productos
  Then el sistema debe retornar error 400
  And el mensaje debe indicar "El precio debe ser mayor a 0"
```

### Especificación 4: Registro con categoría inválida

```gherkin
Scenario: Intento de registro con categoría no permitida
  Given estoy autenticado como cuidador
  When envío la solicitud POST /api/productos con categoria "veterinaria"
  Then el sistema debe retornar error 400
  And el mensaje debe indicar "Categoría inválida"
```

## HU-02: Edición o Eliminación de Producto/Servicio (Ofertante)

**Como** Ofertante **Quiero** modificar mis servicios **Para** mantener actualizada mi oferta

### Especificación 5: Edición crítica (precio) - cambia estado a pendiente

```gherkin
Scenario: Edición del precio de un servicio aprobado
  Given tengo un servicio aprobado con precio 50.00
  When modifico el precio a 60.00
  Then el sistema debe actualizar el servicio
  And el estado del servicio debe cambiar a "pendiente"
  And el servicio debe necesitar nueva validación
  And el código de respuesta debe ser 200
```

### Especificación 6: Edición crítica (título) - cambia estado a pendiente

```gherkin
Scenario: Edición del título de un servicio aprobado
  Given tengo un servicio aprobado con título "Paseo mañanero"
  When modifico el título a "Paseo completo"
  Then el sistema debe actualizar el servicio
  And el estado del servicio debe cambiar a "pendiente"
```

### Especificación 7: Edición no crítica - mantiene estado

```gherkin
Scenario: Edición solo de descripción de un servicio aprobado
  Given tengo un servicio aprobado
  When modifico solo la descripción del servicio
  Then el sistema debe actualizar el servicio
  And el estado del servicio debe permanecer "aprobado"
  And el código de respuesta debe ser 200
```

### Especificación 8: Eliminación exitosa de servicio

```gherkin
Scenario: Eliminación exitosa de un servicio
  Given tengo un servicio registrado
  When envío la solicitud DELETE /api/productos/{id}
  Then el sistema debe marcar el servicio como inactivo (soft delete)
  And el servicio no debe aparecer en listados
  And el código de respuesta debe ser 200
```

### Especificación 9: Eliminación de servicio inexistente

```gherkin
Scenario: Intento de eliminar servicio que no existe
  Given no existe un servicio con ID 9999
  When envío la solicitud DELETE /api/productos/9999
  Then el sistema debe retornar error 404
  And el mensaje debe indicar "Producto no encontrado"
```

## HU-03: Validación de Contenido (Administrador)

**Como** Administrador **Quiero** revisar productos pendientes **Para** garantizar la calidad de la plataforma

### Especificación 10: Aprobación exitosa de servicio pendiente

```gherkin
Scenario: Aprobación exitosa de un servicio
  Given estoy autenticado como administrador
  And existe un servicio en estado "pendiente"
  When envío la solicitud PUT /api/productos/{id}/validar con estado "aprobado"
  Then el sistema debe cambiar el estado a "aprobado"
  And el servicio debe ser visible para demandantes
  And el código de respuesta debe ser 200
```

### Especificación 11: Rechazo de servicio con motivo

```gherkin
Scenario: Rechazo de servicio con motivo
  Given estoy autenticado como administrador
  And existe un servicio en estado "pendiente"
  When envío la solicitud PUT /api/productos/{id}/validar con:
    | estado        | rechazado |
    | motivo_rechazo| Precio no competitivo |
  Then el sistema debe cambiar el estado a "rechazado"
  And el motivo de rechazo debe quedar registrado
  And el servicio no debe ser visible para demandantes
  And el código de respuesta debe ser 200
```

### Especificación 12: Rechazo sin motivo (caso borde)

```gherkin
Scenario: Intento de rechazo sin proporcionar motivo
  Given estoy autenticado como administrador
  And existe un servicio en estado "pendiente"
  When envío la solicitud PUT /api/productos/{id}/validar con estado "rechazado" sin motivo
  Then el sistema debe retornar error 400
  And el mensaje debe indicar "Debe proporcionar un motivo de rechazo"
```

### Especificación 13: Aprobar servicio ya aprobado

```gherkin
Scenario: Intento de aprobar servicio ya aprobado
  Given estoy autenticado como administrador
  And existe un servicio en estado "aprobado"
  When envío la solicitud PUT /api/productos/{id}/validar con estado "aprobado"
  Then el sistema debe retornar éxito (200)
  And el estado debe permanecer "aprobado"
```

## Resumen de Cobertura de Specs

| Tipo de caso | Especificaciones | Cobertura |
|--------------|------------------|-----------|
| Happy Path (éxito) | #1, #5, #7, #8, #10, #11 | ✅ 6 |
| Casos de borde | #4, #6, #9, #13 | ✅ 4 |
| Validaciones/Errores | #2, #3, #12 | ✅ 3 |
| **Total** | **13 especificaciones** | **✅ 100%** |