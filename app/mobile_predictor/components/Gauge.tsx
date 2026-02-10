import React from 'react';
import { View, StyleSheet, Text, Dimensions } from 'react-native';
import Svg, { Path, G, Circle, Text as SvgText, Line, Defs, LinearGradient, Stop } from 'react-native-svg';

interface GaugeProps {
  value: number;
  label: string;
  isDarkMode?: boolean;
}

export const Gauge: React.FC<GaugeProps> = ({ value, label, isDarkMode }) => {
  // Dimensions
  const SCREEN_WIDTH = Dimensions.get('window').width;
  // Calculate size based on screen width but cap it for tablets/web
  const MAX_WIDTH = 350;
  const SIZE = Math.min(SCREEN_WIDTH * 0.9, MAX_WIDTH); // Responsive size
  const VIEWBOX_SIZE = 300; // Internal coordinate system size
  const CX = VIEWBOX_SIZE / 2;
  const CY = VIEWBOX_SIZE / 2 + 20; // Push center down slightly
  const R = 120; // Radius of the arc
  const STROKE_WIDTH = 25;
  
  // Colors
  const textColor = isDarkMode ? '#FFFFFF' : '#333333';
  const labelColor = isDarkMode ? '#AAAAAA' : '#666666';
  const needleColor = isDarkMode ? '#FFFFFF' : '#2D3436';
  const pivotColor = isDarkMode ? '#E0E0E0' : '#2D3436';
  const tickColor = isDarkMode ? 'rgba(255,255,255,0.3)' : 'rgba(0,0,0,0.2)';

  // Ranges with colors - Equal 20% segments
  const ranges = [
    { min: 0, max: 20, color: "#FF4136" },   // Extreme Fear (Red)
    { min: 20, max: 40, color: "#FF851B" },  // Fear (Orange)
    { min: 40, max: 60, color: "#FFDC00" },  // Neutral (Yellow)
    { min: 60, max: 80, color: "#2ECC40" },  // Greed (Light Green)
    { min: 80, max: 100, color: "#01FF70" }, // Extreme Greed (Green)
  ];

  // --- Helpers ---

  // Map value 0-100 to angle 180 to 360 (180 degree span, top half)
  const valueToAngle = (val: number) => {
    const clamped = Math.min(Math.max(val, 0), 100);
    return 180 + (clamped / 100) * 180;
  };

  // Convert polar to cartesian
  const polarToCartesian = (cx: number, cy: number, r: number, angleDeg: number) => {
    const rad = (angleDeg * Math.PI) / 180;
    return {
      x: cx + r * Math.cos(rad),
      y: cy + r * Math.sin(rad),
    };
  };

  // Create SVG Arc Path
  const describeArc = (cx: number, cy: number, r: number, startAngle: number, endAngle: number) => {
    const start = polarToCartesian(cx, cy, r, endAngle); // SVG path direction
    const end = polarToCartesian(cx, cy, r, startAngle);
    const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
    
    return [
      "M", start.x, start.y,
      "A", r, r, 0, largeArcFlag, 0, end.x, end.y
    ].join(" ");
  };

  // --- Render Components ---

  // 1. Color Arcs
  const renderArcs = () => {
    return ranges.map((range, i) => {
      const startAngle = valueToAngle(range.min);
      const endAngle = valueToAngle(range.max);
      // Add a tiny gap between segments for a "segmented" look, or 0 for smooth
      const gap = 1; 
      
      return (
        <Path
          key={`arc-${i}`}
          d={describeArc(CX, CY, R, startAngle + (i === 0 ? 0 : gap), endAngle - (i === ranges.length - 1 ? 0 : gap))}
          fill="none"
          stroke={range.color}
          strokeWidth={STROKE_WIDTH}
          strokeLinecap="butt"
        />
      );
    });
  };

  // 2. Ticks (0, 25, 50, 75, 100)
  const renderTicks = () => {
    const ticks = [0, 25, 50, 75, 100];
    return ticks.map((t, i) => {
      const angle = valueToAngle(t);
      // Outer ticks
      const start = polarToCartesian(CX, CY, R + STROKE_WIDTH/2 + 2, angle);
      const end = polarToCartesian(CX, CY, R + STROKE_WIDTH/2 + 8, angle);
      
      return (
        <Line
          key={`tick-${i}`}
          x1={start.x}
          y1={start.y}
          x2={end.x}
          y2={end.y}
          stroke={tickColor}
          strokeWidth="2"
        />
      );
    });
  };

  // 3. Tick Labels (0 and 100)
  const renderTickLabels = () => {
    const startPos = polarToCartesian(CX, CY, R + STROKE_WIDTH/2 + 20, 180);
    const endPos = polarToCartesian(CX, CY, R + STROKE_WIDTH/2 + 20, 360);
    
    return (
      <>
        <SvgText
          x={startPos.x}
          y={startPos.y}
          fill={labelColor}
          fontSize="12"
          fontWeight="bold"
          textAnchor="middle"
          alignmentBaseline="middle"
        >
          0
        </SvgText>
        <SvgText
          x={endPos.x}
          y={endPos.y}
          fill={labelColor}
          fontSize="12"
          fontWeight="bold"
          textAnchor="middle"
          alignmentBaseline="middle"
        >
          100
        </SvgText>
      </>
    );
  };

  // 4. Needle
  const renderNeedle = () => {
    const angle = valueToAngle(value);
    const needleLen = R - 10;
    const tip = polarToCartesian(CX, CY, needleLen, angle);
    
    // Needle base (perpindicular to angle)
    const baseW = 6;
    const rad = (angle * Math.PI) / 180;
    const perpAngle = rad + Math.PI / 2;
    
    const x1 = CX + baseW * Math.cos(perpAngle);
    const y1 = CY + baseW * Math.sin(perpAngle);
    const x2 = CX - baseW * Math.cos(perpAngle);
    const y2 = CY - baseW * Math.sin(perpAngle);

    return (
      <G>
        {/* Needle Shape */}
        <Path
          d={`M ${x1} ${y1} L ${tip.x} ${tip.y} L ${x2} ${y2} Z`}
          fill={needleColor}
          stroke={needleColor}
          strokeWidth="1"
        />
        {/* Pivot Circle */}
        <Circle cx={CX} cy={CY} r="8" fill={pivotColor} />
        <Circle cx={CX} cy={CY} r="3" fill={isDarkMode ? "#333" : "#FFF"} />
      </G>
    );
  };

  return (
    <View style={[styles.container, { width: SIZE }]}>
      <Svg
        width={SIZE}
        height={SIZE * 0.6} // Aspect ratio for semi-circle + text
        viewBox={`0 0 ${VIEWBOX_SIZE} ${VIEWBOX_SIZE * 0.6}`}
      >
        {/* Background Track (optional, looks cleaner with just segments) */}
        
        {/* Color Segments */}
        {renderArcs()}
        
        {/* Ticks & Labels */}
        {renderTicks()}
        {renderTickLabels()}
        
        {/* Needle */}
        {renderNeedle()}
      </Svg>
      
      {/* Value & Label Text */}
      <View style={styles.textContainer}>
        <Text style={[styles.valueText, { color: textColor }]}>{value}</Text>
        <Text style={[styles.labelText, { color: labelColor }]}>{label}</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: 5,
  },
  textContainer: {
    alignItems: 'center',
    marginTop: -10,
  },
  valueText: {
    fontSize: 36,
    fontWeight: '800',
    fontVariant: ['tabular-nums'],
  },
  labelText: {
    fontSize: 16,
    fontWeight: '600',
    marginTop: 2,
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
});

export default Gauge;
