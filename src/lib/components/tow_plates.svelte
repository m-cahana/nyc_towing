<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';
  import Scrolly from "$lib/components/helpers/scrolly.svelte";
  import { getFullPath } from '$lib/utils/paths';

  // Props for the component
  let {
        dataPath = '/data/plates_to_tow_daily_sample.csv',
        width = 800,
        height = 500,
        CIRCLE_RADIUS = 5,
        CIRCLE_OPACITY = 0.8,
        selectedPlate = 'KUB5440',
        sidePlates = ['KHD6094', 'MJF5321', 
        'LFM4533', 'KZB6485', 'LAC2752', 
        'K72RCF', 'JSF2653', 'KEE6882'],
        margin = { top: 20, right: 20, bottom: 100, left: 60 },
    } = $props();

  let topPlates;
  let svg;
  const innerHeight = height - margin.top - margin.bottom;
  let data = [];
  let container;
  let hasAnimated = false;
  let x; // Make x scale accessible to all functions
  let nodes;
  let plateViolations = new Map(); // Store violations for each plate
  let mainGroup; // Add mainGroup to module scope

  // Scrolly state
  let currentSection = $state(0);
  let previousSection = 0;

  // Define scroll sections
  const scrollSections = [
    {
      title: "",
      content: "Let's look at data from August 2024, for example. <span style='background-color: var(--primary-blue); color: white;'>Each day this month, nearly 100 speeders entered judgment</span>, and show no record of later getting booted or towed."
    },
    {
      title: "",
      content: "If we track this phenomenon over the course of a year, we see a consistent pattern: nearly a hundred speeders a day enter judgment and successfully evade enforcement, translating to <span style='background-color: var(--primary-blue); color: white;'>nearly 30,000 plates a year</span>."
    },
    {
      title: "",
      content: "Since these plates don't get booted or towed, they're free to continue speeding. <span style='background-color: var(--worst-offenders); color: white;'>Many of them (colored in dark blue) speed again after entering judgment."
    },
    {
      title: "",
      content: "In fact, <span style='background-color: var(--worst-offenders); color: white;'>50% of these drivers keep speeding after entering judgment</span>, committing violations that would have never happened if the city comprehensively enforced the law."
    }, 
    {
      title: "",
      content: "Here's an example of a driver who kept on speeding long after entering judgment. If you click on dots to the right, you can view a few other examples."
    }
  ];

  // Function to regenerate axes
  function regenerateAxes(filteredData, dateFormat = "%B") {
    if (!filteredData || filteredData.length === 0) return null;

    // Calculate new domains
    const dateExtent = d3.extent(filteredData, d => d.tow_eligible_date);
    if (!dateExtent[0] || !dateExtent[1]) return null;

    const maxPlatesPerDate = d3.max(filteredData, d => d.n_plates);
    
    // Round up max plates to nearest 5
    const roundedMax = Math.ceil(maxPlatesPerDate / 5) * 5;
    
    // Update scales
    console.log(dateExtent);
    x.domain(dateExtent);

    const y = d3.scaleLinear()
      .domain([0, roundedMax])
      .range([height - margin.bottom, margin.top]);
    
    // Calculate appropriate number of ticks
    const yTickCount = Math.min(10, Math.ceil(roundedMax / 5));
    
    svg.select('.x-axis')
      .transition()
      .duration(500)
      .call(d3.axisBottom(x)
        .ticks(10)
        .tickFormat(d3.timeFormat(dateFormat)));
    
    svg.select('.y-axis')
      .transition()
      .duration(500)
      .call(d3.axisLeft(y)
        .ticks(yTickCount));
    
    return { x, y }; // Return the new y scale for use in updating points
  }

  // Function to create the visualization
  function createVisualization() {
    if (!container || hasAnimated) return;

    // Create SVG
    svg = d3.select(container)
    .append('svg')
    .attr('viewBox', [0, 0, width, height])
    .attr('preserveAspectRatio', 'xMidYMid meet')
    .style('width', '100%')
    .style('height', 'auto')
    .style('overflow', 'visible');


    // Add a clip path to prevent overflow in sections 0-3
    svg.append('defs')
      .append('clipPath')
      .attr('id', 'plot-clip')
      .append('rect')
      .attr('width', width)
      .attr('height', height);

    // Apply clip path to main group
    mainGroup = svg.append('g')
      .attr('clip-path', 'url(#plot-clip)');

    // Filter data for August 2024
    const augustData = data.filter(d => d.tow_eligible_date.getMonth() === 7 && d.tow_eligible_date.getFullYear() === 2024);

    
    // Add axes first with August-specific domain
    x = d3.scaleTime()
      .domain(d3.extent(augustData, d => d.tow_eligible_date))
      .range([margin.left, width - margin.right]);

    const roundedMax = Math.ceil(Math.max(...augustData.map(d => d.n_plates)) / 5) * 5;

    const y = d3.scaleLinear()
      .domain([0, roundedMax])
      .range([height - margin.bottom, margin.top]);

    // Create axis groups with August-specific formatting
    svg.append('g')
      .attr('class', 'x-axis axis')
      .attr('transform', `translate(0,${height - margin.bottom})`)
      .call(d3.axisBottom(x)
        .tickFormat(d3.timeFormat("%b %d")));

    // Add x-axis label
    svg.append('text')
      .attr('class', 'axis-label')
      .attr('text-anchor', 'middle')
      .attr('x', width / 2)
      .attr('y', innerHeight + margin.bottom - 10)
      .text('Date');

    svg.append('g')
      .attr('class', 'y-axis axis')
      .attr('transform', `translate(${margin.left},0)`)
      .call(d3.axisLeft(y));

    // Add y-axis label
    svg.append('text')
      .attr('class', 'axis-label')
      .attr('text-anchor', 'middle')
      .attr('transform', `rotate(-90) translate(${-innerHeight/2}, ${-margin.left + 75})`)
      .text('Number of plates entering judgment');

    topPlates = data;

    nodes = mainGroup.selectAll('circle')
      .data(topPlates)
      .enter()
      .append('circle')
      .attr("cx", function (d) {
        return x(d.tow_eligible_date);
      })
      .attr("cy", function (d) {
        return y(d.n_plates);
      })
      .attr('r', CIRCLE_RADIUS)
      .attr('fill', 'var(--primary-blue)')
      .attr('opacity', d => (d.tow_eligible_date.getMonth() === 7 && d.tow_eligible_date.getFullYear() === 2024) ? CIRCLE_OPACITY : 0)
      .attr('class', 'leaf-circle')
      .on('mouseover', function(event, d) {
        const isWorstOffender = d3.select(this).attr('fill') === 'var(--worst-offenders)';
        d3.select(this)
          .classed("leaf-circle-hover", !isWorstOffender)
          .classed("worst-offenders-hover", isWorstOffender);
          // Create or update tooltip
          const tooltip = d3.select(container)
            .selectAll(".tooltip")
            .data([null])
            .join("div")
            .attr("class", "tooltip");
          
          const tooltipContent = `
            <strong>Plate ID:</strong> ${d.plate}<br>
            <strong>State:</strong> ${d.state}
            <br>
            <strong>License type:</strong> ${d.license_type}
            <br>
            <strong>Eligible to be towed starting:</strong> ${d.tow_eligible_date.toLocaleDateString()}<br>
            <strong>One of ${d.n_plates} plates </strong> that became tow-eligible on this date
          `;
          
          tooltip
            .html(tooltipContent)
            .style("left", `${event.clientX + 15}px`)
            .style("top", `${event.clientY - 40}px`)
            .style("opacity", 1);
        })
        .on("mouseout", function() {
          d3.select(this)
            .classed("leaf-circle-hover", false)
            .classed("worst-offenders-hover", false);
          d3.select(container)
            .selectAll(".tooltip")
            .style("opacity", 0);
        })
        .on("mousemove", function(event) {
          d3.select(container)
            .selectAll(".tooltip")
            .style("left", `${event.clientX + 15}px`)
            .style("top", `${event.clientY - 40}px`);
        });
      };

  // Function to load plate violations
  async function loadPlateViolations(plate) {
    const violationsPath = `/data/fines_plate_${plate}.csv`;
    try {
      const response = await fetch(getFullPath(violationsPath));
      const csvText = await response.text();
      const violations = d3.csvParse(csvText, d => ({
        ...d,
        violation_date: new Date(d.issue_date),
        is_paid: parseFloat(d.amount_due) === 0
      }));
      plateViolations.set(plate, violations);
    } catch (error) {
      console.error(`Error loading violations for plate ${plate}:`, error);
    }
  }

  onMount(async () => {
    // Load and process the data
    const fullDataPath = getFullPath(dataPath);
    console.log(`Loading data from: ${fullDataPath}`);
    
    d3.csv(fullDataPath)
      .then(rawData => {
        // Convert dates and filter for 2024, with error handling
        data = rawData
          .filter(d => d && d.tow_eligible_date) // Filter out any null/undefined entries
          .map(d => ({
            ...d,
            tow_eligible_date: new Date(d.tow_eligible_date),
            n_plates: parseInt(d.n_plates)
          }))
          .filter(d => !isNaN(d.tow_eligible_date.getTime())) 
          .sort((a, b) => a.tow_eligible_date - b.tow_eligible_date);
        
        // Create visualization immediately
        createVisualization();
      })
      .catch((error) => {
        console.error("Error loading CSV:", error);
      });
  });

  // Function to update visualization based on scroll section
  async function updateVisualization(currentSection) {
    if (!svg || !data || data.length === 0) return;


    // Add different effects based on the current section
    if (currentSection === 0) {

      // Filter data for August 2024
      const augustData = data.filter(d => d.tow_eligible_date.getMonth() === 7 && d.tow_eligible_date.getFullYear() === 2024);
      const { x: xScale, y: yScale } = regenerateAxes(augustData, "%b %d");

      // Create a line generator for connecting circles
      const connectLine = d3.line()
        .x(d => xScale(d.tow_eligible_date))
        .y(d => yScale(d.n_plates))
        .curve(d3.curveMonotoneX);

      // Add or update the connecting line
      svg.selectAll('.connect-line').remove(); // Remove existing line if any

      svg.append('path')
        .attr('class', 'connect-line')
        .datum(augustData)
        .attr('d', connectLine)
        .attr('fill', 'none')
        .attr('stroke', 'var(--primary-blue)')
        .attr('stroke-width', 2)
        .attr('opacity', 0)
        .transition()
        .duration(500)
        .attr('opacity', 0.5);
      
      // Update opacity using the nodes object
      nodes
        .transition()
        .duration(500)
        .attr('cx', d => xScale(d.tow_eligible_date))
        .attr('cy', d => yScale(d.n_plates))
        .attr('opacity', (d) => (d.tow_eligible_date.getMonth() === 7 && d.tow_eligible_date.getFullYear() === 2024) ? CIRCLE_OPACITY : 0)
        .attr('fill', 'var(--primary-blue)');
    }
      
    // full year
    else if (currentSection === 1) {
      // Reset to full view
      const { x: xScale, y: yScale } = regenerateAxes(data, "%b %Y");
      if (!yScale) return;
      
      // Show axes and labels again
      svg.selectAll('.x-axis, .y-axis, .axis-label')
        .transition()
        .duration(500)
        .attr('opacity', 1);
      
      // Remove stack labels
      svg.selectAll('.stack-label')
        .transition()
        .duration(500)
        .attr('opacity', 0)
        .remove();
      
      // Remove the connecting line
      svg.selectAll('.connect-line')
        .transition()
        .duration(500)
        .attr('opacity', 0)
        .remove();
      
      // Update points - select the date groups and rebind data
      const dateGroups = d3.group(data, d => d.tow_eligible_date);
      const dateEntries = Array.from(dateGroups.entries());
      
      // Create rolling 90-day average data
      const rollingAverageData = data.map((d, i) => {
        // Get the previous 90 days of data (or fewer if at the start)
        const startIdx = Math.max(0, i - 89);
        const windowData = data.slice(startIdx, i + 1);
        
        // Calculate average plates per day in the window
        const totalPlates = windowData.reduce((sum, d) => sum + d.n_plates, 0);
        const avgPlates = totalPlates / windowData.length;
        
        return {
          tow_eligible_date: d.tow_eligible_date,
          n_plates: avgPlates
        };
      });

      // Create a line generator for the rolling average
      const connectLine = d3.line()
        .x(d => xScale(d.tow_eligible_date))
        .y(d => yScale(d.n_plates))
        .curve(d3.curveMonotoneX);

      // Add or update the connecting line
      svg.selectAll('.connect-line').remove(); // Remove existing line if any
      svg.append('path')
        .attr('class', 'connect-line')
        .datum(rollingAverageData)
        .attr('d', connectLine)
        .attr('fill', 'none')
        .attr('stroke', 'var(--primary-blue)')
        .attr('stroke-width', 2)
        .attr('opacity', 0)
        .transition()
        .duration(500)
        .attr('opacity', 0.5);
      
      // Update opacity using the nodes object
      nodes
        .transition()
        .duration(500)
        .attr('cx', d => xScale(d.tow_eligible_date))
        .attr('cy', d => yScale(d.n_plates))
        .attr('opacity', CIRCLE_OPACITY)
        .attr('fill', 'var(--primary-blue)');


        svg.selectAll('.divider-label').remove()
    }

    // color worst offenders
    if (currentSection === 2) {
      nodes.transition()
        .duration(500)
        .attr('fill', d => d.violations_post_tow_eligible > 0 ? 'var(--worst-offenders)' : 'var(--primary-blue)')
        .attr('opacity', CIRCLE_OPACITY);

      svg.selectAll('.grid-divider').remove();
      svg.selectAll('.grid-divider-label').remove();
      svg.selectAll('.divider-label').remove(); // Remove any leftover divider labels from section 4
    }

    // split into grid
    if (currentSection === 3) {

    // Hide axes and labels
    svg.selectAll('.x-axis, .y-axis, .axis-label')
      .transition()
      .duration(500)
      .attr('opacity', 0);

    svg.selectAll('.connect-line').remove();
    svg.selectAll('.violation-label,.stack-label, .divider-label, .violation-divider, .title-label').remove();
    svg.selectAll('.divider-label').remove(); // Remove any leftover divider labels from section 4
    svg.style('overflow', 'visible');

    const NODE_SPACING = 20;
    const outerRowLength = 17;
    const middleRowLength = 20;
    const rowLengths = [
      ...Array(9).fill(17),           
      ...Array(3).fill(20),        
      ...Array(9).fill(17)            
    ];
    // Precompute start indices for each row
    const rowStartIndices = rowLengths.reduce((acc, len, i) => {
      const prev = acc[i - 1] || 0;
      acc.push(prev + (i > 0 ? rowLengths[i - 1] : 0));
      return acc;
    }, []);

    function getRowAndColumn(index) {
      let rowIndex = 0;
      for (let i = 0; i < rowStartIndices.length; i++) {
        if (index < rowStartIndices[i]) {
          rowIndex = i - 1;
          break;
        } else if (i === rowStartIndices.length - 1) {
          rowIndex = i;
        }
      }
      const colIndex = index - rowStartIndices[rowIndex];
      return { rowIndex, colIndex };
    }

    const gridWidth = Math.max(outerRowLength, middleRowLength) * NODE_SPACING;
    const gridHeight = rowLengths.length * NODE_SPACING;
    const startX = (width - gridWidth) / 2;
    const startY = (height - gridHeight) / 2;

    // Calculate 50% divider Y position
    const halfIndex = Math.floor(nodes.size() * 0.5);
    const { rowIndex: halfRow } = getRowAndColumn(halfIndex);
    const halfY = startY + halfRow * NODE_SPACING;

    // Draw divider
    svg.append('line')
      .attr('class', 'grid-divider')
      .attr('x1', startX - 15)
      .attr('x2', startX + gridWidth)
      .attr('y1', halfY)
      .attr('y2', halfY)
      .attr('stroke', 'var(--worst-offenders-hover)')
      .attr('stroke-width', 1)
      .attr('stroke-dasharray', '4,4')
      .attr('opacity', 0)
      .transition()
      .duration(500)
      .attr('opacity', 1);

    svg.append('text')
      .attr('class', 'grid-divider-label')
      .attr('x', startX + gridWidth + 10)
      .attr('y', halfY)
      .attr('text-anchor', 'start')
      .attr('dominant-baseline', 'middle')
      .attr('fill', 'var(--worst-offenders-hover)')
      .attr('opacity', 0)
      .text('50%')
      .transition()
      .duration(500)
      .attr('opacity', 1);

    // Sort nodes: blue first, then red
    nodes = nodes.sort((a, b) => {
      const aRed = a.violations_post_tow_eligible > 0;
      const bRed = b.violations_post_tow_eligible > 0;
      return aRed === bRed ? 0 : aRed ? 1 : -1;
    });

    // Reposition nodes
    nodes
      .transition()
      .duration(500)
      .attr('cx', (d, i) => {
        const { rowIndex, colIndex } = getRowAndColumn(i);
        const rowLength = rowLengths[rowIndex];
        const rowStartX = (width - rowLength * NODE_SPACING) / 2;
        return rowStartX + colIndex * NODE_SPACING;
      })
      .attr('cy', (d, i) => {
        const { rowIndex } = getRowAndColumn(i);
        return startY + rowIndex * NODE_SPACING;
      })
      .attr('r', CIRCLE_RADIUS)
      .attr('opacity', CIRCLE_OPACITY)
      .attr('class', 'leaf-circle')
      .style('cursor', 'pointer');

  }

    // zoom in on selected plates
    if (currentSection === 4) {
      // Remove clip path for section 4 to allow overflow
      mainGroup.attr('clip-path', null);
      
      // Hide axes and labels
      svg.selectAll('.x-axis, .y-axis, .axis-label')
        .transition()
        .duration(500)
        .attr('opacity', 0);

      svg.selectAll('.stack-label').remove(); // Remove existing line if any
      svg.selectAll('.grid-divider').remove();
      svg.selectAll('.grid-divider-label').remove();

      // Set SVG to allow overflow
      svg.style('overflow', 'visible');

      // Select the specific plate instead of a random one
      const targetNode = topPlates.find(p => p.plate === selectedPlate);
      console.log(`Selected plate: ${targetNode?.plate}`);
      if (!targetNode) return;

      // Load violations for this plate if not already loaded
      if (!plateViolations.has(targetNode.plate)) {
        await loadPlateViolations(targetNode.plate);
      }
      const violations = plateViolations.get(targetNode.plate) || [];
      const sortedViolations = violations.sort((a, b) => a.violation_date - b.violation_date);

      // Calculate zoom parameters
      const zoomRadius = Math.min(width, height) * 0.67; // Use original height
      const centerX = width / 2;
      const centerY = height / 2; // Use original height

      // Create specificPlatesData array with both selected plate and side plates
      const specificPlatesData = [selectedPlate, ...sidePlates]
        .map(plate => topPlates.find(p => p.plate === plate))
        .filter(Boolean); // Remove any undefined entries

      // Add specific plates to topPlates if they don't exist
      specificPlatesData.forEach(plate => {
        if (!topPlates.find(p => p.plate === plate.plate)) {
          topPlates.push(plate);
        }
      });

      // Update all nodes
      nodes = mainGroup.selectAll('circle')
        .data(topPlates)
        .join('circle')
        .attr('class', d => {
          if (d.plate === targetNode.plate) {
            return 'leaf-circle non-interactive';
          }
          return specificPlatesData.find(p => p.plate === d.plate) ? 'leaf-circle' : 'leaf-circle non-interactive';
        })
        .style('cursor', d => {
          if (d.plate === targetNode.plate) {
            return 'default';
          }
          return specificPlatesData.find(p => p.plate === d.plate) ? 'pointer' : 'default';
        })
        .attr('fill', d => {
          // Preserve worst-offenders coloring for all nodes
          return d.violations_post_tow_eligible > 0 ? 'var(--worst-offenders)' : 'var(--primary-blue)';
        });

      // Position all nodes
      nodes
        .transition()
        .duration(1000)
        .attr('cx', d => {
          if (d.plate === targetNode.plate) {
            return centerX;
          }
          // Position side plates on the right
          const index = specificPlatesData.findIndex(p => p.plate === d.plate);
          if (index !== -1) {
            return centerX + zoomRadius + 50; // Position just outside the zoomed circle
          }
          // Move other nodes off screen
          return -50;
        })
        .attr('cy', d => {
          if (d.plate === targetNode.plate) {
            return centerY;
          }
          // Position side plates vertically
          const index = specificPlatesData.findIndex(p => p.plate === d.plate);
          if (index !== -1) {
            // stack them vertically with 40px spacing, starting from the second position
            const yOffset = (index - 4.5) * 40;
            return centerY + yOffset;
          }
          // Move other nodes off screen
          return -50;
        })
        .attr('r', d => {
          if (d.plate === targetNode.plate) {
            return zoomRadius;
          }
          return specificPlatesData.find(p => p.plate === d.plate) ? CIRCLE_RADIUS * 1.5 : 0; // Slightly larger side nodes
        })
        .attr('opacity', d => {
          // Show both the target node and all specific plates
          if (d.plate === targetNode.plate || specificPlatesData.find(p => p.plate === d.plate)) {
            return CIRCLE_OPACITY;
          }
          return 0;
        });

      // Add click handlers for the side plates
      nodes.filter(d => specificPlatesData.find(p => p.plate === d.plate))
        .on('click', async function(event, d) {
          // Load violations for the clicked plate
          if (!plateViolations.has(d.plate)) {
            await loadPlateViolations(d.plate);
          }
          
          // Store the previous target node before updating
          const previousTarget = targetNode;
          
          // Update selected plate
          selectedPlate = d.plate;
          
          // Ensure the previous target node is in the stack, removing the oldest plate instead of the last one
          if (previousTarget && !sidePlates.includes(previousTarget.plate)) {
            sidePlates = [previousTarget.plate, ...sidePlates.slice(1)];
          }
          
          // Clear all labels and lines
          svg.selectAll('.violation-label').remove();
          svg.selectAll('.violation-divider').remove();
          svg.selectAll('.divider-label').remove();
          svg.selectAll('.connect-line').remove();
          svg.selectAll('.title-label').remove();
          
          // Trigger the visualization update
          updateVisualization(4);
        });

      // Remove any existing violation labels
      svg.selectAll('.violation-label').remove();
      svg.selectAll('.violation-divider').remove();


      const startX = centerX - 220; 
      const lineHeight = 20; 
      const LABELS_PER_LINE = 4;
      const LABEL_SPACING = 55; // pixels between labels on same line

      // Find the index where violations cross the tow-eligible date
      const towEligibleDate = targetNode.tow_eligible_date;
      const dividerIndex = sortedViolations.findIndex(v => v.violation_date > towEligibleDate);

      // Split violations into pre and post tow-eligible, filtering out paid violations
      const preViolations = sortedViolations.slice(0, dividerIndex).filter(v => !v.is_paid);
      const postViolations = sortedViolations.slice(dividerIndex).filter(v => !v.is_paid);

      // Calculate percentage of violations after judgment
      const totalUnpaidViolations = preViolations.length + postViolations.length;
      const postPercentage = totalUnpaidViolations > 0 ? ((postViolations.length / totalUnpaidViolations) * 100).toFixed(0) : 0;

      // Calculate vertical spacing for each half
      const preStartY = centerY - zoomRadius * 0.5; 
      const postStartY = centerY + zoomRadius * 0.2; 
      const labelYOffset = 60;

      // Add title label
      svg.append('text')
        .attr('class', 'title-label')
        .attr('x', centerX - 200)
        .attr('y', preStartY - labelYOffset)
        .attr('text-anchor', 'left')
        .attr('opacity', 0)
        .each(function() {
          const text = d3.select(this);
          text.append('tspan')
            .style('text-decoration', 'underline')
            .text(`${targetNode.plate}'s unpaid tickets`);
          text.append('tspan')
            .attr('dy', '1.2em')
            .attr('x', centerX - 180)
            .style('text-decoration', 'underline')
            .text(`(${postPercentage}% occur after entering judgment)`);
        })
        .transition()
        .duration(500)
        .attr('opacity', 1);

      // Helper function to create violation labels
      function createViolationLabels(violations, startX, startY, startIndex, delayOffset = 0) {
        return svg.selectAll(`.violation-label-${startIndex === 0 ? 'pre' : 'post'}`)
          .data(violations)
          .enter()
          .append('g') // Create a group for each violation
          .attr('class', `violation-label ${startIndex === 0 ? '' : 'post-divider'}`)
          .attr('transform', (d, i) => {
            const lineIndex = Math.floor(i / LABELS_PER_LINE);
            const positionInLine = i % LABELS_PER_LINE;
            const x = startX + (positionInLine * (60 + LABEL_SPACING));
            const y = startY + (lineIndex * lineHeight);
            return `translate(${x},${y})`;
          })
          .attr('opacity', 0)
          .each(function(d, i) {
            const group = d3.select(this);
            
            // Add the violation number and date text
            group.append('text')
              .attr('text-anchor', 'start')
              .each(function() {
                const text = d3.select(this);
                text.append('tspan')
                  .attr('fill', 'var(--worst-offenders-hover)')
                  .text(`${startIndex + i + 1} - `);
                text.append('tspan')
                  .attr('fill', '#ffffff')
                  .style('text-decoration', d.is_paid ? 'line-through' : 'none')
                  .text(d3.timeFormat("%b %d %Y")(d.violation_date));
              });
          })
          .transition()
          .delay((d, i) => delayOffset + (i * 100))
          .duration(500)
          .attr('opacity', 1);
      }

      // Add the dividing line
      svg.append('line')
        .attr('class', 'violation-divider')
        .attr('x1', centerX - zoomRadius)
        .attr('x2', centerX + zoomRadius)
        .attr('y1', centerY)
        .attr('y2', centerY)
        .attr('stroke', 'var(--worst-offenders-hover)')
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', '5,5')
        .attr('opacity', 0)
        .transition()
        .delay(preViolations.length * 100) // Wait for all pre-violations to appear
        .duration(500)
        .attr('opacity', 1)
        .on('end', () => {
          // Add the text label for the divider after the line appears
          const nextDay = new Date(targetNode.tow_eligible_date);
          nextDay.setDate(nextDay.getDate() + 1);
          svg.append('text')
            .attr('class', 'divider-label')
            .attr('x', startX - 30)
            .attr('y', preViolations.length > 32 ? centerY + 20 : centerY - 10)
            .attr('text-anchor', 'left')
            .attr('opacity', 0)
            .text(() => {
              return `${targetNode.plate} enters judgment on ${d3.timeFormat("%B %d, %Y")(nextDay)}`;
            })
            .transition()
            .duration(500)
            .attr('opacity', 1);
        });

      // Create violation labels for pre and post tow-eligible violations
      createViolationLabels(preViolations, startX, preStartY, 0);
      createViolationLabels(postViolations, startX, postStartY, preViolations.length, preViolations.length * 100 + 1000);
    }
  
  }

  // Effect to update visualization when section changes
  $effect(() => {
    if (currentSection !== undefined) {
      updateVisualization(currentSection);
    }
  });
</script>

<section id="scrolly">
  <!-- Background visualization container -->
  <div class="visualization-container" bind:this={container}>
    <!-- The visualization will be rendered here by D3 -->
    <div id="tooltip" class="tooltip"></div>
  </div>
  
  <!-- Spacer to start scrolling below the initial view -->
  <div class="spacer"></div>
  
  <!-- Scrolly component for text sections -->
  <Scrolly bind:value={currentSection}>
    {#each scrollSections as section, i}
      <div class="step" class:active={currentSection === i}>
        <div class="step-content">
          {#if section.title !== ""}<h3>{section.title}</h3>{/if}
          <p>{@html section.content}</p>
        </div>
      </div>
    {/each}
  </Scrolly>
  
  <!-- Spacer at the end to ensure we can scroll to the last section -->
  <div class="spacer"></div>
</section>

<style>
  @import '$lib/../app.css';
  
  #scrolly {
    position: relative;
    width: 100%;
  }
  
  .visualization-container {
    position: sticky;
    top: 0;
    height: 100vh;
    width: 100%;
    z-index: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
  }
  
  /* Tooltip styles */
  :global(.tooltip) {
    opacity: 0;
    transition: opacity 0.2s;
    font-size: 14px;
    font-family: 'Helvetica', sans-serif;
    text-align: left;
    position: fixed;
    background-color: white;
    color: black;
    border-radius: 5px;
    box-shadow: 0 0 10px rgba(0,0,0,0.25);
    border: 1px solid rgba(0,0,0,0.1);
    padding: 10px;
    pointer-events: none;
    font-weight: 300;
    z-index: 9999;
    min-width: 200px;
    max-width: 300px;
  }
  
  :global(strong) {
    font-weight: 450;
  }

  .spacer {
    height: 50vh;
  }
  
  .step {
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 20px;
    position: relative;
    z-index: 2;
    pointer-events: none;
  }
  
  .step-content {
    background-color: rgba(255, 255, 255, 0.9);
    border-radius: 8px;
    padding: 20px;
    max-width: 350px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin: 0 auto;
    pointer-events: auto;
  }

  .step-content h3 {
    margin-top: 0;
    margin-bottom: 0.5em;
    font-weight: 550;
    font-size: 18px;
  }
  
  .step-content p {
    margin: 0;
    font-size: 16px;
    text-align: left;
  }

  circle {
    cursor: pointer;
  }

  :global(.axis text) {
    font-family: Helvetica, Arial, sans-serif;
    font-weight: 300;
    font-size: 14px;
  }

  :global(.x-axis text) {
    transform: rotate(-45deg);
    text-anchor: end;
  }

  /* Circle styles */
  :global(.leaf-circle) {
    stroke: none;
    stroke-width: 0;
  }
  
  :global(.leaf-circle-hover) {
    fill: var(--dark-blue);
    stroke-width: 0.5px;
    stroke: black;
  }

  :global(.worst-offenders-hover) {
    fill: var(--worst-offenders-hover);
  }

  :global(.axis-label) {
    font-family: Helvetica, Arial, sans-serif;
    font-weight: 300;
    font-size: clamp(18px, 1.5vw, 18px);
  }

  :global(.stack-label) {
    font-family: Helvetica, Arial, sans-serif;
    font-weight: 400;
    font-size: 18px;
  }

  :global(.node-label) {
    font-family: Helvetica, Arial, sans-serif;
    font-weight: 400;
    font-size: 18px;
  }

  :global(.divider-label) {
    font-style: italic;
    font-size: 14px;
    fill: #ffffff;
    opacity: 1;
  }

  :global(.violation-label) {
    fill: #ffffff;
    font-size: 14px;
  }

  :global(.violation-label.post-divider) {
    fill: #ffffff;
  }

  :global(.non-interactive) {
    pointer-events: none;
  }

  :global(.title-label) {
    font-size: 16px;
    font-style: italic;
    font-weight: 600;
  }

  :global(.title-label tspan) {
    fill: #ffffff;
  }

</style>
