import React from "react";
import { useCurrentFrame, interpolate, Easing, Img } from "remotion";
import { fontFamily, GlassCard } from "./UI";

// Helper for scene base container with 2D camera floating effect (much faster on headless server CPUs)
const SceneContainer: React.FC<{
  children: React.ReactNode;
  duration: number;
  style?: React.CSSProperties;
}> = ({ children, duration, style }) => {
  const frame = useCurrentFrame();

  // Subtle 2D float movement (zoom + very slow translation)
  const scale = interpolate(frame, [0, duration], [1.01, 1.04], {
    extrapolateRight: "clamp",
  });
  const translateX = interpolate(frame, [0, duration], [-8, 8]);
  const translateY = interpolate(frame, [0, duration], [-4, 4]);
  const opacity = interpolate(frame, [0, 20, duration - 20, duration], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        opacity,
        fontFamily,
        ...style,
      }}
    >
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          transform: `scale(${scale}) translate(${translateX}px, ${translateY}px)`,
        }}
      >
        {children}
      </div>
    </div>
  );
};

// -------------------------------------------------------------
// ESCENA 1: APERTURA (0-10s) - Zarvent Repuestos
// -------------------------------------------------------------
export const Scene1Apertura: React.FC<{ logoUrl: string }> = ({ logoUrl }) => {
  const frame = useCurrentFrame();

  // Element anims
  const logoScale = interpolate(frame, [0, 45], [0.5, 1], {
    easing: Easing.bezier(0.16, 1, 0.3, 1),
    extrapolateRight: "clamp",
  });
  const logoOpacity = interpolate(frame, [0, 30], [0, 1]);
  const titleOpacity = interpolate(frame, [25, 55], [0, 1], { extrapolateLeft: "clamp" });
  const subtitleOpacity = interpolate(frame, [45, 75], [0, 1], { extrapolateLeft: "clamp" });
  const techOpacity = interpolate(frame, [70, 100], [0, 1], { extrapolateLeft: "clamp" });

  return (
    <SceneContainer duration={300}>
      <div style={{ textAlign: "center", transform: "translateZ(50px)" }}>
        {/* Animated Logo Container */}
        <div
          style={{
            transform: `scale(${logoScale})`,
            opacity: logoOpacity,
            marginBottom: "30px",
            display: "inline-block",
            filter: "drop-shadow(0 0 30px rgba(0, 242, 254, 0.4))",
          }}
        >
          <Img
            src={logoUrl}
            alt="Zarvent Logo"
            style={{ width: "220px", height: "220px", borderRadius: "32px" }}
          />
        </div>

        {/* Title */}
        <h1
          style={{
            opacity: titleOpacity,
            fontSize: "80px",
            fontWeight: 800,
            letterSpacing: "-2px",
            background: "linear-gradient(135deg, #f8fafc 30%, #00f2fe 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            margin: "0 0 10px 0",
          }}
        >
          ZARVENT REPUESTOS
        </h1>

        {/* Subtitle */}
        <p
          style={{
            opacity: subtitleOpacity,
            fontSize: "30px",
            color: "#94a3b8",
            fontWeight: 400,
            letterSpacing: "4px",
            textTransform: "uppercase",
            margin: "0 0 60px 0",
          }}
        >
          Gestión Relacional de Autopartes
        </p>

        {/* Technology Badges */}
        <div
          style={{
            opacity: techOpacity,
            display: "flex",
            justifyContent: "center",
            gap: "24px",
          }}
        >
          {["MySQL Server", "Python 3", "Flask", "bcrypt"].map((tech, idx) => (
            <div
              key={idx}
              style={{
                background: "rgba(11, 20, 38, 0.4)",
                border: "1px solid rgba(0, 242, 254, 0.3)",
                borderRadius: "12px",
                padding: "10px 24px",
                fontSize: "18px",
                fontWeight: 600,
                color: "#00f2fe",
                boxShadow: "0 5px 15px rgba(0, 0, 0, 0.2)",
              }}
            >
              {tech}
            </div>
          ))}
        </div>
      </div>
    </SceneContainer>
  );
};

// -------------------------------------------------------------
// ESCENA 2: PROBLEMA MANUAL (10-25s) - Desorganización
// -------------------------------------------------------------
export const Scene2Problema: React.FC = () => {
  const frame = useCurrentFrame();
  const duration = 450;

  // Render 6 problem labels floating around chaotically
  const problems = [
    { text: "Clientes Duplicados", delay: 30, x: -350, y: -200, color: "#ef4444" },
    { text: "Hojas de Papel / Recibos Sueltos", delay: 60, x: 380, y: -160, color: "#f97316" },
    { text: "WhatsApp desorganizado", delay: 90, x: -420, y: 50, color: "#facc15" },
    { text: "Stock Fantasma / Agotados", delay: 120, x: 400, y: 120, color: "#ef4444" },
    { text: "Excel Desactualizado", delay: 150, x: -180, y: 220, color: "#f97316" },
    { text: "Precios inconsistentes", delay: 180, x: 250, y: 240, color: "#facc15" },
  ];

  return (
    <SceneContainer duration={duration}>
      <div style={{ position: "relative", width: "100%", height: "100%", display: "flex", justifyContent: "center", alignItems: "center" }}>
        
        {/* Warning Symbol in the Center */}
        <div
          style={{
            width: "300px",
            height: "300px",
            borderRadius: "50%",
            background: "rgba(239, 68, 68, 0.08)",
            border: "2px dashed rgba(239, 68, 68, 0.4)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            boxShadow: "0 0 60px rgba(239, 68, 68, 0.1)",
            transform: `rotate(${frame * 0.1}deg)`,
          }}
        >
          <div
            style={{
              width: "160px",
              height: "160px",
              borderRadius: "50%",
              background: "linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              boxShadow: "0 10px 30px rgba(239, 68, 68, 0.4)",
              transform: `scale(${interpolate(frame, [0, 30], [0.5, 1], { easing: Easing.bounce, extrapolateRight: "clamp" })})`,
            }}
          >
            {/* Warning Sign icon */}
            <svg width="70" height="70" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
              <line x1="12" y1="9" x2="12" y2="13" />
              <line x1="12" y1="17" x2="12.01" y2="17" />
            </svg>
          </div>
        </div>

        {/* Text explaining the problem */}
        <div style={{ position: "absolute", top: "80px", textAlign: "center" }}>
          <h2 style={{ fontSize: "50px", fontWeight: 700, color: "#ef4444", marginBottom: "10px" }}>
            EL DESAFÍO DEL CONTROL MANUAL
          </h2>
          <p style={{ fontSize: "22px", color: "#94a3b8", letterSpacing: "1px" }}>
            La desorganización que frena el crecimiento comercial
          </p>
        </div>

        {/* Floating Problem Cards */}
        {problems.map((prob, idx) => {
          if (frame < prob.delay) return null;
          
          // Animate entry from the center out
          const entryProgress = interpolate(frame, [prob.delay, prob.delay + 30], [0, 1], {
            easing: Easing.bezier(0.16, 1, 0.3, 1),
            extrapolateRight: "clamp",
          });
          
          const currentX = prob.x * entryProgress;
          const currentY = prob.y * entryProgress;
          const cardScale = entryProgress;
          
          // Subtle hover float after entry
          const floatOffset = Math.sin((frame - prob.delay) * 0.05) * 8;

          return (
            <div
              key={idx}
              style={{
                position: "absolute",
                transform: `translate3d(${currentX}px, ${currentY + floatOffset}px, 20px) scale(${cardScale})`,
                background: "rgba(11, 20, 38, 0.8)",
                border: `1.5px solid ${prob.color}66`,
                borderRadius: "16px",
                padding: "18px 30px",
                color: "#f8fafc",
                fontSize: "20px",
                fontWeight: 600,
                boxShadow: `0 10px 25px rgba(0, 0, 0, 0.3), 0 0 15px ${prob.color}22`,
                pointerEvents: "none",
              }}
            >
              <span style={{ marginRight: "10px", color: prob.color }}>●</span>
              {prob.text}
            </div>
          );
        })}
      </div>
    </SceneContainer>
  );
};

// -------------------------------------------------------------
// ESCENA 3: ACTORES Y FLUJO DEL NEGOCIO (25-42s)
// -------------------------------------------------------------
export const Scene3Actores: React.FC = () => {
  const frame = useCurrentFrame();
  const duration = 510;

  // 5 main actors in the relational structure
  const actors = [
    { role: "Vendedor Técnico", desc: "Verifica compatibilidad vehicular, marcas y códigos", icon: "🔧", x: -450, y: -80 },
    { role: "Cajero de Facturación", desc: "Registra cobros vinculados directamente a ventas reales", icon: "💳", x: -150, y: 150 },
    { role: "Encargado de Almacén", desc: "Controla existencias físicas por ubicación y stock mínimo", icon: "📦", x: 150, y: 150 },
    { role: "Responsable de Compras", desc: "Abastece repuestos agotados y coordina proveedores", icon: "🛒", x: 450, y: -80 },
    { role: "Administrador / Gerente", desc: "Supervisa ventas diarias y repuestos con stock bajo", icon: "📊", x: 0, y: -210 },
  ];

  return (
    <SceneContainer duration={duration}>
      <div style={{ position: "relative", width: "100%", height: "100%", display: "flex", justifyContent: "center", alignItems: "center" }}>
        
        {/* Title */}
        <div style={{ position: "absolute", top: "80px", textAlign: "center" }}>
          <h2 style={{ fontSize: "50px", fontWeight: 700, color: "#00f2fe", marginBottom: "10px" }}>
            ROLES Y FLUJO OPERATIVO
          </h2>
          <p style={{ fontSize: "22px", color: "#94a3b8" }}>
            Organización relacional sin redundancia de responsabilidades
          </p>
        </div>

        {/* Central Database Hub */}
        <div
          style={{
            position: "absolute",
            width: "180px",
            height: "180px",
            borderRadius: "50%",
            background: "rgba(0, 242, 254, 0.05)",
            border: "3px solid #00f2fe",
            boxShadow: "0 0 40px rgba(0, 242, 254, 0.2), inset 0 0 20px rgba(0, 242, 254, 0.1)",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
            zIndex: 10,
            transform: `scale(${interpolate(frame, [0, 45], [0.6, 1], { easing: Easing.bezier(0.16, 1, 0.3, 1), extrapolateRight: "clamp" })})`,
          }}
        >
          <span style={{ fontSize: "42px" }}>🖧</span>
          <span style={{ fontSize: "16px", fontWeight: 700, color: "#00f2fe", marginTop: "5px", letterSpacing: "1px" }}>BASE DE DATOS</span>
          <span style={{ fontSize: "12px", color: "#94a3b8" }}>CENTRALIZADA</span>
        </div>

        {/* Connective lines and actor cards */}
        {actors.map((actor, idx) => {
          const delay = idx * 40 + 30;
          if (frame < delay) return null;

          const entryProgress = interpolate(frame, [delay, delay + 30], [0, 1], {
            easing: Easing.bezier(0.16, 1, 0.3, 1),
            extrapolateRight: "clamp",
          });

          const cardX = actor.x;
          const cardY = actor.y;

          return (
            <React.Fragment key={idx}>
              {/* Connecting Line SVG */}
              <svg
                style={{
                  position: "absolute",
                  top: 0,
                  left: 0,
                  width: "100%",
                  height: "100%",
                  pointerEvents: "none",
                  zIndex: 2,
                }}
              >
                <line
                  x1="960" // screen center X
                  y1="540" // screen center Y
                  x2={960 + cardX * entryProgress}
                  y2={540 + cardY * entryProgress}
                  stroke="#00f2fe"
                  strokeWidth="2"
                  strokeDasharray="5 5"
                  opacity={entryProgress * 0.4}
                />
              </svg>

              {/* Actor Card */}
              <div
                style={{
                  position: "absolute",
                  transform: `translate3d(${cardX}px, ${cardY}px, 30px) scale(${entryProgress})`,
                  width: "260px",
                  background: "rgba(11, 20, 38, 0.75)",
                  border: "1px solid rgba(0, 242, 254, 0.2)",
                  borderRadius: "16px",
                  padding: "20px",
                  boxShadow: "0 15px 35px rgba(0, 0, 0, 0.4)",
                  zIndex: 5,
                  textAlign: "center",
                }}
              >
                <div style={{ fontSize: "36px", marginBottom: "8px" }}>{actor.icon}</div>
                <h3 style={{ fontSize: "20px", fontWeight: 700, color: "#fff", marginBottom: "6px" }}>{actor.role}</h3>
                <p style={{ fontSize: "13px", color: "#94a3b8", lineHeight: "1.4" }}>{actor.desc}</p>
              </div>
            </React.Fragment>
          );
        })}
      </div>
    </SceneContainer>
  );
};

// -------------------------------------------------------------
// ESCENA 4: EL ERD Y ENTIDADES CENTRALES (42-65s)
// -------------------------------------------------------------
export const Scene4Erd: React.FC = () => {
  const frame = useCurrentFrame();
  const duration = 690;

  // Simplified entity nodes for the scene
  const entities = [
    { name: "PERSON", cols: ["person_id (PK)", "first_name", "last_name", "identity_number (UK)", "phone"], x: -480, y: -160, color: "#4facfe" },
    { name: "CUSTOMER", cols: ["customer_id (PK)", "person_id (FK)", "billing_name", "tax_id"], x: -160, y: -160, color: "#4facfe" },
    { name: "SALES_ORDER", cols: ["sales_order_id (PK)", "customer_id (FK)", "order_date", "total_amount"], x: 160, y: -160, color: "#00f2fe" },
    { name: "SALES_ORDER_ITEM", cols: ["sales_order_item_id (PK)", "sales_order_id (FK)", "part_id (FK)", "quantity", "unit_price"], x: 480, y: -160, color: "#00f2fe" },
    
    { name: "PART_CATEGORY", cols: ["part_category_id (PK)", "name (UK)"], x: -320, y: 150, color: "#10b981" },
    { name: "PART", cols: ["part_id (PK)", "part_category_id (FK)", "internal_code (UK)", "sale_price", "purchase_cost"], x: 0, y: 150, color: "#10b981" },
    { name: "INVENTORY_STOCK", cols: ["inventory_stock_id (PK)", "part_id (FK)", "quantity_on_hand", "location_name"], x: 320, y: 150, color: "#10b981" },
  ];

  return (
    <SceneContainer duration={duration}>
      <div style={{ position: "relative", width: "100%", height: "100%", display: "flex", justifyContent: "center", alignItems: "center" }}>
        
        {/* Title */}
        <div style={{ position: "absolute", top: "70px", textAlign: "center" }}>
          <h2 style={{ fontSize: "50px", fontWeight: 700, color: "#00f2fe", marginBottom: "5px" }}>
            DIAGRAMA ENTIDAD-RELACIÓN
          </h2>
          <p style={{ fontSize: "20px", color: "#94a3b8" }}>
            Estructura operativa normalizada y libre de redundancias
          </p>
        </div>

        {/* Relationship lines */}
        <svg
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "100%",
            height: "100%",
            pointerEvents: "none",
            zIndex: 1,
          }}
        >
          {/* Drawing relational links dynamically */}
          {frame > 100 && (
            <>
              {/* PERSON -> CUSTOMER (1:1) */}
              <path d="M 640 380 L 800 380" stroke="#4facfe" strokeWidth="2.5" fill="none" opacity={0.6} />
              
              {/* CUSTOMER -> SALES_ORDER (1:N) */}
              <path d="M 960 380 L 1120 380" stroke="#00f2fe" strokeWidth="2.5" fill="none" opacity={0.6} />
              
              {/* SALES_ORDER -> SALES_ORDER_ITEM (1:N) */}
              <path d="M 1280 380 L 1440 380" stroke="#00f2fe" strokeWidth="2.5" fill="none" opacity={0.6} />

              {/* PART_CATEGORY -> PART (1:N) */}
              <path d="M 800 690 L 960 690" stroke="#10b981" strokeWidth="2.5" fill="none" opacity={0.6} />

              {/* PART -> INVENTORY_STOCK (1:1) */}
              <path d="M 1120 690 L 1280 690" stroke="#10b981" strokeWidth="2.5" fill="none" opacity={0.6} />

              {/* PART -> SALES_ORDER_ITEM (1:N) */}
              <path d="M 960 635 L 960 580 L 1440 580 L 1440 435" stroke="#facc15" strokeWidth="2" strokeDasharray="6 4" fill="none" opacity={0.5} />
            </>
          )}
        </svg>

        {/* Entities container */}
        {entities.map((ent, idx) => {
          const delay = idx * 20 + 20;
          if (frame < delay) return null;

          const entryProgress = interpolate(frame, [delay, delay + 20], [0, 1], {
            easing: Easing.bezier(0.16, 1, 0.3, 1),
            extrapolateRight: "clamp",
          });

          return (
            <div
              key={idx}
              style={{
                position: "absolute",
                transform: `translate3d(${ent.x}px, ${ent.y}px, 30px) scale(${entryProgress})`,
                width: "250px",
                background: "rgba(11, 20, 38, 0.9)",
                border: `1.5px solid ${ent.color}77`,
                borderRadius: "14px",
                overflow: "hidden",
                boxShadow: "0 10px 25px rgba(0, 0, 0, 0.4)",
                zIndex: 5,
              }}
            >
              {/* Header */}
              <div
                style={{
                  background: ent.color,
                  padding: "8px 15px",
                  color: "#060913",
                  fontWeight: 700,
                  fontSize: "16px",
                  letterSpacing: "1px",
                  display: "flex",
                  justifyContent: "space-between",
                }}
              >
                <span>{ent.name}</span>
                <span style={{ fontSize: "12px", opacity: 0.8 }}>📋</span>
              </div>
              {/* Columns */}
              <div style={{ padding: "12px", background: "rgba(11, 20, 38, 0.6)" }}>
                {ent.cols.map((col, cIdx) => (
                  <div
                    key={cIdx}
                    style={{
                      fontSize: "13px",
                      color: col.includes("(PK)") ? "#facc15" : col.includes("(FK)") ? "#00f2fe" : "#e2e8f0",
                      padding: "4px 0",
                      fontWeight: col.includes("(PK)") || col.includes("(FK)") ? 600 : 400,
                      textAlign: "left",
                    }}
                  >
                    {col.includes("(PK)") ? "🔑 " : col.includes("(FK)") ? "🔗 " : "  "}
                    {col}
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </SceneContainer>
  );
};

// -------------------------------------------------------------
// ESCENA 5: INTEGRIDAD EN MYSQL Y PRECIO HISTÓRICO (65-90s)
// -------------------------------------------------------------
export const Scene5Integridad: React.FC = () => {
  const frame = useCurrentFrame();
  const duration = 750;

  // SQL snippet to render
  const sqlCode = `CREATE TABLE sales_order_item (
    sales_order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    sales_order_id      INT NOT NULL,
    part_id             INT NOT NULL,
    quantity            INT NOT NULL,
    unit_price          DECIMAL(10, 2) NOT NULL, -- PRECIO HISTÓRICO
    FOREIGN KEY (sales_order_id) REFERENCES sales_order(id),
    FOREIGN KEY (part_id) REFERENCES part(part_id)
);`;

  const sqlTyping = Math.floor(interpolate(frame, [40, 200], [0, sqlCode.length], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  }));

  const sqlVisible = sqlCode.slice(0, sqlTyping);

  // Animation for the price rule comparison
  const step = Math.floor(interpolate(frame, [230, 350, 480, 600], [0, 1, 2, 3], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  }));

  return (
    <SceneContainer duration={duration}>
      <div style={{ width: "90%", height: "80%", display: "flex", gap: "40px", alignItems: "center", transform: "translateZ(40px)" }}>
        
        {/* Left Side: Code Editor */}
        <div style={{ flex: 1.2, height: "100%", display: "flex", flexDirection: "column" }}>
          <h3 style={{ fontSize: "24px", color: "#00f2fe", fontWeight: 700, marginBottom: "15px", textAlign: "left" }}>
            🔑 INTEGRIDAD OPERATIVA (DDL)
          </h3>
          <div
            style={{
              flex: 1,
              background: "#050811",
              border: "1px solid rgba(255, 255, 255, 0.1)",
              borderRadius: "16px",
              padding: "24px",
              fontFamily: "monospace",
              fontSize: "15px",
              color: "#e2e8f0",
              textAlign: "left",
              whiteSpace: "pre-wrap",
              boxShadow: "0 15px 30px rgba(0, 0, 0, 0.4)",
              overflow: "hidden",
            }}
          >
            {/* Window header */}
            <div style={{ display: "flex", gap: "8px", marginBottom: "20px" }}>
              <div style={{ width: "12px", height: "12px", borderRadius: "50%", background: "#ef4444" }}></div>
              <div style={{ width: "12px", height: "12px", borderRadius: "50%", background: "#facc15" }}></div>
              <div style={{ width: "12px", height: "12px", borderRadius: "50%", background: "#22c55e" }}></div>
              <span style={{ color: "#94a3b8", fontSize: "12px", marginLeft: "10px" }}>schema.sql</span>
            </div>
            
            {/* SQL Content */}
            <code style={{ color: "#a5b4fc" }}>
              {sqlVisible}
              {sqlTyping < sqlCode.length && (
                <span style={{ color: "#00f2fe", animation: "blink 1s infinite" }}>|</span>
              )}
            </code>
          </div>
        </div>

        {/* Right Side: Historical Price visual explainer */}
        <div style={{ flex: 1, height: "100%", display: "flex", flexDirection: "column", justifyContent: "center" }}>
          <h3 style={{ fontSize: "24px", color: "#facc15", fontWeight: 700, marginBottom: "20px", textAlign: "left" }}>
            💰 REGLA: PRECIO HISTÓRICO
          </h3>

          <GlassCard style={{ padding: "30px", flex: 1, display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
            {/* Step 0: Initial state */}
            <div style={{ opacity: step >= 0 ? 1 : 0.25 }}>
              <div style={{ fontWeight: 700, fontSize: "17px", color: "#38bdf8", marginBottom: "5px" }}>
                1. Catálogo de Repuestos
              </div>
              <div style={{ fontSize: "15px", color: "#94a3b8", display: "flex", justifyContent: "space-between" }}>
                <span>Repuesto: Pastilla Freno</span>
                <span style={{ color: "#fff", fontWeight: 600 }}>Precio: $45.00</span>
              </div>
            </div>

            {/* Arrow */}
            <div style={{ textAlign: "center", color: "#00f2fe", fontSize: "20px", opacity: step >= 1 ? 1 : 0.2 }}>↓</div>

            {/* Step 1: Sale created */}
            <div style={{ opacity: step >= 1 ? 1 : 0.25 }}>
              <div style={{ fontWeight: 700, fontSize: "17px", color: "#38bdf8", marginBottom: "5px" }}>
                2. Venta Registrada (Enero)
              </div>
              <div style={{ fontSize: "15px", color: "#94a3b8", display: "flex", justifyContent: "space-between" }}>
                <span>Sales_Order_Item</span>
                <span style={{ color: "#22c55e", fontWeight: 600 }}>Unit_Price: $45.00</span>
              </div>
            </div>

            {/* Arrow */}
            <div style={{ textAlign: "center", color: "#ef4444", fontSize: "20px", opacity: step >= 2 ? 1 : 0.2 }}>↓</div>

            {/* Step 2: Price changes in Catalog */}
            <div style={{ opacity: step >= 2 ? 1 : 0.25 }}>
              <div style={{ fontWeight: 700, fontSize: "17px", color: "#ef4444", marginBottom: "5px" }}>
                3. Actualización de Catálogo (Marzo)
              </div>
              <div style={{ fontSize: "15px", color: "#94a3b8", display: "flex", justifyContent: "space-between" }}>
                <span>Repuesto: Pastilla Freno</span>
                <span style={{ color: "#ef4444", fontWeight: 600 }}>Nuevo Precio: $52.00</span>
              </div>
            </div>

            {/* Arrow */}
            <div style={{ textAlign: "center", color: "#22c55e", fontSize: "20px", opacity: step >= 3 ? 1 : 0.2 }}>↓</div>

            {/* Step 3: Consistency preserved */}
            <div style={{ opacity: step >= 3 ? 1 : 0.25 }}>
              <div style={{ fontWeight: 700, fontSize: "17px", color: "#22c55e", marginBottom: "5px" }}>
                4. Consistencia Preservada
              </div>
              <div style={{ fontSize: "15px", color: "#e2e8f0" }}>
                Venta de Enero se mantiene en <span style={{ color: "#facc15", fontWeight: 600 }}>$45.00</span> sin alterarse por la inflación. ¡Auditoría íntegra!
              </div>
            </div>
          </GlassCard>
        </div>
      </div>
    </SceneContainer>
  );
};

// -------------------------------------------------------------
// ESCENA 6: DEMO VISUAL - INTERFAZ FLASK (90-118s)
// -------------------------------------------------------------
export const Scene6Demo: React.FC = () => {
  const frame = useCurrentFrame();
  const duration = 840;

  // Animating values inside the dashboard
  const salesCount = Math.floor(interpolate(frame, [60, 200], [10, 184], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  }));
  const revenueTotal = Math.floor(interpolate(frame, [60, 220], [1000, 14850], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  }));

  // Visual state triggers
  const showDetail = frame > 250;
  const showRecibo = frame > 550;

  return (
    <SceneContainer duration={duration}>
      <div style={{ width: "95%", height: "85%", display: "flex", flexDirection: "column", transform: "translateZ(30px)" }}>
        {/* Top Header of Simulated Web App */}
        <div
          style={{
            background: "rgba(11, 20, 38, 0.9)",
            border: "1px solid rgba(255, 255, 255, 0.08)",
            borderBottom: "none",
            borderTopLeftRadius: "16px",
            borderTopRightRadius: "16px",
            padding: "15px 30px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <span style={{ fontSize: "24px" }}>🚗</span>
            <span style={{ fontWeight: 700, fontSize: "20px", color: "#fff", letterSpacing: "1px" }}>ZARVENT SYSTEM</span>
            <span style={{ background: "rgba(0,242,254,0.1)", color: "#00f2fe", fontSize: "11px", padding: "3px 8px", borderRadius: "8px", fontWeight: 600 }}>FLASK APPLICATION</span>
          </div>
          <div style={{ display: "flex", gap: "20px", fontSize: "14px", color: "#94a3b8" }}>
            <span style={{ color: "#00f2fe", fontWeight: 600 }}>Dashboard</span>
            <span>Repuestos</span>
            <span>Clientes</span>
            <span>Ventas</span>
            <div style={{ borderLeft: "1px solid rgba(255,255,255,0.1)", paddingLeft: "15px", display: "flex", alignItems: "center", gap: "6px" }}>
              <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#22c55e" }}></span>
              <span style={{ color: "#fff" }}>vendedor_tecnico</span>
            </div>
          </div>
        </div>

        {/* Main Interface Content */}
        <div
          style={{
            flex: 1,
            background: "#080c16",
            border: "1px solid rgba(255, 255, 255, 0.08)",
            borderBottomLeftRadius: "16px",
            borderBottomRightRadius: "16px",
            display: "flex",
            padding: "24px",
            gap: "24px",
          }}
        >
          {/* Left Side: Main Dashboard Info */}
          <div style={{ flex: 1.8, display: "flex", flexDirection: "column", gap: "20px" }}>
            
            {/* KPI Cards row */}
            <div style={{ display: "flex", gap: "20px" }}>
              {/* Total sales KPI */}
              <div style={{ flex: 1, background: "rgba(11,20,38,0.5)", border: "1px solid rgba(255,255,255,0.05)", borderRadius: "12px", padding: "18px", textAlign: "left" }}>
                <span style={{ fontSize: "13px", color: "#94a3b8", textTransform: "uppercase" }}>Ventas Totales</span>
                <h4 style={{ fontSize: "32px", fontWeight: 700, color: "#fff", margin: "5px 0" }}>{salesCount}</h4>
                <span style={{ fontSize: "12px", color: "#22c55e" }}>↑ 12% este mes</span>
              </div>
              {/* Total Revenue KPI */}
              <div style={{ flex: 1, background: "rgba(11,20,38,0.5)", border: "1px solid rgba(255,255,255,0.05)", borderRadius: "12px", padding: "18px", textAlign: "left" }}>
                <span style={{ fontSize: "13px", color: "#94a3b8", textTransform: "uppercase" }}>Ingresos (Bs.)</span>
                <h4 style={{ fontSize: "32px", fontWeight: 700, color: "#00f2fe", margin: "5px 0" }}>Bs. {revenueTotal.toLocaleString()}</h4>
                <span style={{ fontSize: "12px", color: "#22c55e" }}>↑ 15.4% de margen</span>
              </div>
            </div>

            {/* Low stock table view (vw_low_stock_parts) */}
            <div style={{ flex: 1, background: "rgba(11,20,38,0.5)", border: "1px solid rgba(255,255,255,0.05)", borderRadius: "12px", padding: "20px", display: "flex", flexDirection: "column" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                <span style={{ fontWeight: 700, color: "#ef4444", fontSize: "16px" }}>⚠️ ALERTAS DE REORDEN (vw_low_stock_parts)</span>
                <span style={{ color: "#94a3b8", fontSize: "12px" }}>Vista Activa en BD</span>
              </div>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "14px", color: "#e2e8f0" }}>
                <thead>
                  <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.08)", color: "#94a3b8", textAlign: "left" }}>
                    <th style={{ padding: "8px" }}>Código</th>
                    <th style={{ padding: "8px" }}>Repuesto</th>
                    <th style={{ padding: "8px" }}>Almacén</th>
                    <th style={{ padding: "8px" }}>Stock</th>
                    <th style={{ padding: "8px" }}>Nivel Reorden</th>
                    <th style={{ padding: "8px" }}>Acción</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { code: "PA-FR-02", name: "Pastilla Freno Delantera", loc: "A-04", stock: 3, reorder: 10, highlight: frame > 120 },
                    { code: "FI-AC-01", name: "Filtro de Aceite Sintético", loc: "B-12", stock: 2, reorder: 8, highlight: frame > 180 },
                    { code: "BU-CH-08", name: "Bujía Precalentamiento", loc: "A-09", stock: 5, reorder: 15, highlight: frame > 240 },
                  ].map((part, idx) => (
                    <tr key={idx} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)", background: part.highlight ? "rgba(239,68,68,0.04)" : "transparent" }}>
                      <td style={{ padding: "10px 8px", fontWeight: 600 }}>{part.code}</td>
                      <td style={{ padding: "10px 8px" }}>{part.name}</td>
                      <td style={{ padding: "10px 8px", color: "#00f2fe" }}>{part.loc}</td>
                      <td style={{ padding: "10px 8px", color: "#ef4444", fontWeight: 700 }}>{part.stock} pcs</td>
                      <td style={{ padding: "10px 8px" }}>{part.reorder} pcs</td>
                      <td style={{ padding: "10px 8px" }}>
                        <span style={{ fontSize: "11px", background: "rgba(239,68,68,0.15)", color: "#ef4444", padding: "2px 6px", borderRadius: "4px", fontWeight: 600 }}>Comprar</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Right Side: Interactive Panel (Detail / Receipt) */}
          <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
            {/* Dynamic Card for Sale creation / Invoice */}
            <div style={{ flex: 1, background: "rgba(11,20,38,0.8)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "12px", padding: "20px", display: "flex", flexDirection: "column", justifyContent: "space-between", textAlign: "left" }}>
              {!showDetail ? (
                // 1. Initial State - Sales Order Creator view
                <div style={{ display: "flex", flexDirection: "column", height: "100%", justifyContent: "center", alignItems: "center", color: "#94a3b8" }}>
                  <span style={{ fontSize: "48px", marginBottom: "15px" }}>🛒</span>
                  <p style={{ fontWeight: 600, fontSize: "16px", color: "#fff" }}>Módulo de Ventas</p>
                  <p style={{ fontSize: "13px", textAlign: "center", padding: "0 20px" }}>Generando transacción en tiempo real en la base de datos...</p>
                </div>
              ) : !showRecibo ? (
                // 2. Mid State - Item additions
                <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                  <span style={{ fontSize: "13px", color: "#00f2fe", fontWeight: 700, letterSpacing: "1px" }}>NUEVA TRANSACCIÓN</span>
                  <h5 style={{ fontSize: "18px", color: "#fff", fontWeight: 700, margin: 0 }}>Venta #1209 - Cliente: C. Pérez</h5>
                  
                  <div style={{ borderTop: "1px solid rgba(255,255,255,0.1)", paddingTop: "10px", display: "flex", flexDirection: "column", gap: "8px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", color: "#e2e8f0" }}>
                      <span>1x Pastilla Freno Delantera</span>
                      <span style={{ fontWeight: 600 }}>Bs. 313.00</span>
                    </div>
                    {frame > 350 && (
                      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", color: "#e2e8f0" }}>
                        <span>2x Filtro Aceite Sintético</span>
                        <span style={{ fontWeight: 600 }}>Bs. 120.00</span>
                      </div>
                    )}
                    {frame > 450 && (
                      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", color: "#e2e8f0" }}>
                        <span>Descuento Aplicado</span>
                        <span style={{ color: "#ef4444" }}>-Bs. 20.00</span>
                      </div>
                    )}
                  </div>
                  
                  <div style={{ borderTop: "1.5px solid #00f2fe", paddingTop: "10px", marginTop: "15px", display: "flex", justifyContent: "space-between", fontWeight: 700, fontSize: "16px" }}>
                    <span style={{ color: "#00f2fe" }}>TOTAL A COBRAR</span>
                    <span style={{ color: "#fff" }}>Bs. {frame > 450 ? "413.00" : frame > 350 ? "433.00" : "313.00"}</span>
                  </div>
                </div>
              ) : (
                // 3. Final State - Digital Receipt / Invoice Printed
                <div style={{ display: "flex", flexDirection: "column", gap: "10px", background: "#f8fafc", color: "#0f172a", padding: "18px", borderRadius: "8px", boxShadow: "0 10px 20px rgba(0,0,0,0.3)", height: "92%", justifyContent: "space-between" }}>
                  <div style={{ textAlign: "center", borderBottom: "1.5px dashed #cbd5e1", paddingBottom: "10px" }}>
                    <h6 style={{ fontSize: "16px", fontWeight: 800, margin: 0 }}>ZARVENT REPUESTOS</h6>
                    <span style={{ fontSize: "10px", color: "#64748b" }}>Fecha: 10/06/2026 - Recibo #004581</span>
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: "6px", fontSize: "12px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between" }}>
                      <span>1x Pastilla Freno</span>
                      <span>Bs. 313.00</span>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between" }}>
                      <span>2x Filtro Aceite</span>
                      <span>Bs. 120.00</span>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", color: "#dc2626" }}>
                      <span>Descuento</span>
                      <span>-Bs. 20.00</span>
                    </div>
                  </div>
                  <div style={{ borderTop: "1.5px dashed #cbd5e1", paddingTop: "8px", display: "flex", justifyContent: "space-between", fontWeight: 800, fontSize: "14px" }}>
                    <span>TOTAL PAGADO</span>
                    <span>Bs. 413.00</span>
                  </div>
                  <div style={{ textAlign: "center", fontSize: "11px", color: "#64748b" }}>
                    <span style={{ display: "block" }}>Método: Transferencia QR</span>
                    <span style={{ display: "block", color: "#059669", fontWeight: 700, marginTop: "5px" }}>✓ PAGO REGISTRADO EN BD</span>
                  </div>
                </div>
              )}
              
              <div style={{ display: "flex", gap: "10px", marginTop: "10px" }}>
                <div style={{ flex: 1, padding: "8px", borderRadius: "6px", background: showRecibo ? "#10b981" : "#00f2fe", color: "#060913", fontWeight: 700, fontSize: "12px", textAlign: "center" }}>
                  {showRecibo ? "OPERACIÓN COMPLETA" : "PROCESAR EN CAJA"}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </SceneContainer>
  );
};

// -------------------------------------------------------------
// ESCENA 7: ALCANCE HONESTO (118-137s)
// -------------------------------------------------------------
export const Scene7Alcance: React.FC = () => {
  const frame = useCurrentFrame();
  const duration = 570;

  return (
    <SceneContainer duration={duration}>
      <div style={{ width: "90%", height: "80%", display: "flex", flexDirection: "column", justifyContent: "center", transform: "translateZ(40px)" }}>
        
        {/* Title */}
        <div style={{ textAlign: "center", marginBottom: "40px" }}>
          <h2 style={{ fontSize: "50px", fontWeight: 700, color: "#facc15", marginBottom: "10px" }}>
            ALCANCE HONESTO DEL PROTOTIPO
          </h2>
          <p style={{ fontSize: "22px", color: "#94a3b8" }}>
            Diferencias claves entre el prototipo y la arquitectura completa propuesta
          </p>
        </div>

        {/* Side-by-Side Comparison */}
        <div style={{ display: "flex", gap: "40px" }}>
          {/* Card 1: Actual Implementation */}
          <div style={{ flex: 1, transform: `translateX(${interpolate(frame, [0, 45], [-150, 0], { easing: Easing.bezier(0.16, 1, 0.3, 1), extrapolateRight: "clamp" })}px)` }}>
            <GlassCard style={{ border: "1.5px solid rgba(16, 185, 129, 0.4)", height: "300px", display: "flex", flexDirection: "column", justifyContent: "space-between", textAlign: "left" }}>
              <div>
                <span style={{ fontSize: "12px", background: "rgba(16, 185, 129, 0.15)", color: "#10b981", padding: "4px 10px", borderRadius: "8px", fontWeight: 700, letterSpacing: "1px" }}>
                  PROTOTIPO OPERATIVO (FLASK)
                </span>
                <h4 style={{ fontSize: "24px", color: "#fff", fontWeight: 700, margin: "15px 0 10px 0" }}>Validación de Conceptos</h4>
                <ul style={{ paddingLeft: "20px", color: "#cbd5e1", fontSize: "15px", lineHeight: "1.7" }}>
                  <li>Creación de Base de Datos y migración relacional</li>
                  <li>Inicio de sesión seguro para usuarios registrados</li>
                  <li>Registro de Clientes y Catálogo de repuestos</li>
                  <li>Creación de ventas con su detalle operativo</li>
                </ul>
              </div>
              <div style={{ fontSize: "14px", color: "#10b981", fontWeight: 600 }}>
                ✓ 100% Defendible por el equipo académico
              </div>
            </GlassCard>
          </div>

          {/* Card 2: ERD Full Reach */}
          <div style={{ flex: 1, transform: `translateX(${interpolate(frame, [0, 45], [150, 0], { easing: Easing.bezier(0.16, 1, 0.3, 1), extrapolateRight: "clamp" })}px)` }}>
            <GlassCard style={{ border: "1.5px solid rgba(0, 242, 254, 0.4)", height: "300px", display: "flex", flexDirection: "column", justifyContent: "space-between", textAlign: "left" }}>
              <div>
                <span style={{ fontSize: "12px", background: "rgba(0, 242, 254, 0.15)", color: "#00f2fe", padding: "4px 10px", borderRadius: "8px", fontWeight: 700, letterSpacing: "1px" }}>
                  DISEÑO FÍSICO COMPLETO (ERD)
                </span>
                <h4 style={{ fontSize: "24px", color: "#fff", fontWeight: 700, margin: "15px 0 10px 0" }}>Escalabilidad Futura</h4>
                <ul style={{ paddingLeft: "20px", color: "#cbd5e1", fontSize: "15px", lineHeight: "1.7" }}>
                  <li>Gestión de compatibilidades de marcas y modelos</li>
                  <li>Control de proveedores y compras de reposición</li>
                  <li>Registro formal de garantías y devoluciones de piezas</li>
                  <li>Sistema de auditoría de movimientos de stock</li>
                </ul>
              </div>
              <div style={{ fontSize: "14px", color: "#00f2fe", fontWeight: 600 }}>
                🛠 Modelado relacional completo en schema.sql
              </div>
            </GlassCard>
          </div>
        </div>
      </div>
    </SceneContainer>
  );
};

// -------------------------------------------------------------
// ESCENA 8: CIERRE ACADÉMICO (137-150s)
// -------------------------------------------------------------
export const Scene8Cierre: React.FC<{ logoUrl: string }> = ({ logoUrl }) => {
  const frame = useCurrentFrame();

  const logoScale = interpolate(frame, [0, 50], [0.6, 1.1], {
    easing: Easing.bezier(0.16, 1, 0.3, 1),
    extrapolateRight: "clamp",
  });
  const logoRotate = interpolate(frame, [0, 390], [0, 15]);

  return (
    <SceneContainer duration={390}>
      <div style={{ textAlign: "center", transform: "translateZ(50px)" }}>
        {/* Rotating Logo */}
        <div
          style={{
            transform: `scale(${logoScale}) rotate(${logoRotate}deg)`,
            marginBottom: "40px",
            display: "inline-block",
            filter: "drop-shadow(0 0 40px rgba(0, 242, 254, 0.5))",
          }}
        >
          <Img
            src={logoUrl}
            alt="Zarvent Logo"
            style={{ width: "200px", height: "200px", borderRadius: "32px" }}
          />
        </div>

        {/* Closing Title */}
        <h2
          style={{
            fontSize: "65px",
            fontWeight: 800,
            background: "linear-gradient(135deg, #f8fafc 40%, #00f2fe 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            margin: "0 0 15px 0",
          }}
        >
          Zarvent Repuestos
        </h2>

        {/* Academic Details */}
        <p style={{ fontSize: "26px", color: "#94a3b8", fontWeight: 500, margin: "0 0 5px 0" }}>
          Proyecto Final - Base de Datos I (SIS-122)
        </p>
        <p style={{ fontSize: "20px", color: "#00f2fe", fontWeight: 600, letterSpacing: "1px", margin: "0 0 40px 0" }}>
          Docente: Prof. Ismael Antonio Delgado Huanca
        </p>

        {/* Final message */}
        <div
          style={{
            display: "inline-block",
            background: "rgba(11, 20, 38, 0.4)",
            border: "1px solid rgba(255, 255, 255, 0.08)",
            borderRadius: "14px",
            padding: "12px 36px",
            fontSize: "18px",
            color: "#f8fafc",
            fontWeight: 400,
            letterSpacing: "2px",
          }}
        >
          MUCHAS GRACIAS POR SU ATENCIÓN
        </div>
      </div>
    </SceneContainer>
  );
};
