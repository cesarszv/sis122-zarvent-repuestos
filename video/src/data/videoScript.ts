export interface Scene {
  id: string;
  title: string;
  subtitle: string;
  narration: string;
  startFrame: number;
  endFrame: number;
  durationFrames: number;
}

export const videoScript: Scene[] = [
  {
    id: "apertura",
    title: "Zarvent Repuestos",
    subtitle: "Gestión Relacional de Autopartes",
    narration: "Bienvenidos a Zarvent Repuestos, un sistema de gestión relacional diseñado para la administración y control de inventario y ventas en tiendas de repuestos automotrices.",
    startFrame: 0,
    endFrame: 300,
    durationFrames: 300,
  },
  {
    id: "problema",
    title: "El Desafío de la Desorganización",
    subtitle: "El caos del control manual",
    narration: "En el día a día, las tiendas de repuestos sufren problemas de desorganización: hojas sueltas, chats de WhatsApp, hojas de Excel desactualizadas, clientes duplicados y stock inexistente. Esto genera pérdidas y frustración en la atención al cliente.",
    startFrame: 300,
    endFrame: 750,
    durationFrames: 450,
  },
  {
    id: "actores",
    title: "Actores y Flujo del Negocio",
    subtitle: "Roles funcionales y responsabilidades",
    narration: "Para solucionar esto, estructuramos un flujo operativo claro. Desde que el cliente solicita una pieza, el vendedor técnico verifica la compatibilidad vehicular, el cajero procesa el pago y el encargado de almacén gestiona el stock físico.",
    startFrame: 750,
    endFrame: 1260,
    durationFrames: 510,
  },
  {
    id: "erd",
    title: "Modelo Entidad-Relación",
    subtitle: "Entidades centrales de Zarvent",
    narration: "La base de datos se modela bajo el estándar relacional. Entidades centrales como personas, clientes, proveedores, repuestos y categorías aseguran que la información no se duplique y se mantenga consistente en todo momento.",
    startFrame: 1260,
    endFrame: 1950,
    durationFrames: 690,
  },
  {
    id: "integridad",
    title: "Integridad y Reglas en MySQL",
    subtitle: "Consistencia de datos y precio histórico",
    narration: "Implementado en MySQL Server, el esquema garantiza integridad mediante claves primarias y foráneas. Además, el detalle de venta almacena el precio unitario histórico para proteger los datos financieros ante futuros cambios de precio.",
    startFrame: 1950,
    endFrame: 2700,
    durationFrames: 750,
  },
  {
    id: "demo",
    title: "Prototipo Operacional",
    subtitle: "Dashboard e interfaz de usuario en Flask",
    narration: "A través de nuestra interfaz en Flask y Python, el personal accede de forma segura. El dashboard dinámico muestra el resumen diario de ventas y repuestos con stock bajo el umbral de reorden mediante vistas optimizadas.",
    startFrame: 2700,
    endFrame: 3540,
    durationFrames: 840,
  },
  {
    id: "alcance",
    title: "Alcance del Proyecto",
    subtitle: "Prototipo funcional vs Modelo completo",
    narration: "El prototipo actual implementa las operaciones esenciales del modelo físico propuesto, validando el comportamiento de las tablas y asegurando que las reglas del negocio relacionales se cumplan estrictamente.",
    startFrame: 3540,
    endFrame: 4110,
    durationFrames: 570,
  },
  {
    id: "cierre",
    title: "Conclusiones",
    subtitle: "Sólidos fundamentos de bases de datos",
    narration: "Zarvent Repuestos demuestra el valor de un diseño relacional sólido como base para sistemas empresariales confiables, escalables y eficientes. Muchas gracias por su atención.",
    startFrame: 4110,
    endFrame: 4500,
    durationFrames: 390,
  },
];
