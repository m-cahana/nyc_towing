<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';
  import Scrolly from "$lib/components/helpers/scrolly.svelte";

  // Constants
  const CIRCLE_RADIUS = 5;
  const CIRCLE_OPACITY = 0.8;

  let svg;
  let width = 800;
  let height = 500;
  let margin = { top: 20, right: 20, bottom: 100, left: 60 };
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;
  let data = [];
  let container;
  let hasAnimated = false;
  let x; // Make x scale accessible to all functions
  let xAxis; // Make axis objects accessible
  let yAxis;
  let nodes;

  // Scrolly state
  let currentSection = $state(0);
  let previousSection = 0;

  // Define scroll sections
  const scrollSections = [
    {
      title: "",
      content: "Let's look at when vehicles become eligible for towing in 2024."
    },
    {
      title: "",
      content: "Let's focus on August 2024, when many vehicles become eligible for towing."
    },
    {
      title: "",
      content: "The height of each stack shows how many vehicles become eligible on that day."
    },
    {
      title: "",
      content: "Hover over any dot to see the plate details."
    }
  ];

  // Function to regenerate axes
  function regenerateAxes(filteredData, dateFormat = "%B") {
    if (!filteredData || filteredData.length === 0) return null;

    // Calculate new domains
    const dateExtent = d3.extent(filteredData, d => d.tow_eligible_date);
    if (!dateExtent[0] || !dateExtent[1]) return null;

    const dateGroups = d3.group(filteredData, d => d.tow_eligible_date);
    const maxPlatesPerDate = d3.max(Array.from(dateGroups.values()), plates => plates.length);
    
    // Round up max plates to nearest 5
    const roundedMax = Math.ceil(maxPlatesPerDate / 5) * 5;
    
    // Update scales
    x.domain(dateExtent);
    const y = d3.scaleLinear()
      .domain([0, roundedMax])
      .range([height - margin.bottom, margin.top]);
    
    // Calculate appropriate number of ticks
    const xTickCount = Math.min(10, dateExtent[1].getDate() - dateExtent[0].getDate() + 1);
    const yTickCount = Math.min(10, Math.ceil(roundedMax / 5));
    
    // Update axes with transitions
    svg.select('.x-axis')
      .transition()
      .duration(500)
      .call(d3.axisBottom(x)
        .ticks(xTickCount)
        .tickFormat(d3.timeFormat(dateFormat)));
    
    svg.select('.y-axis')
      .transition()
      .duration(500)
      .call(d3.axisLeft(y)
        .ticks(yTickCount));
    
    return y; // Return the new y scale for use in updating points
  }

  // Function to create the visualization
  function createVisualization() {
    if (!container || hasAnimated) return;

    // Create SVG
    svg = d3.select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height);

    // Add axes first
    x = d3.scaleTime()
      .domain(d3.extent(data, d => d.tow_eligible_date))
      .range([margin.left, width - margin.right]);

    const dateGroups = d3.group(data, d => d.tow_eligible_date);
    const maxPlatesPerDate = d3.max(Array.from(dateGroups.values()), plates => plates.length);
    const roundedMax = Math.ceil(maxPlatesPerDate / 5) * 5;

    const y = d3.scaleLinear()
      .domain([0, roundedMax])
      .range([height - margin.bottom, margin.top]);

    // Create axis groups
    svg.append('g')
      .attr('class', 'x-axis axis')
      .attr('transform', `translate(0,${height - margin.bottom})`)
      .call(d3.axisBottom(x)
        .tickFormat(d3.timeFormat("%B")));

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
      .text('Number of plates entering judgement');

    // Plot points for each date group with animation
    const dateEntries = Array.from(dateGroups.entries());

    // Calculate average plates per day
    const totalPlates = data.length;
    const totalDays = dateEntries.length;
    const averagePlatesPerDay = totalPlates / totalDays;

    // Create a line generator for the average
    const line = d3.line()
      .x(d => x(d.date))
      .y(() => y(averagePlatesPerDay))
      .curve(d3.curveMonotoneX);

    // Create line data
    const lineData = dateEntries.map(([date]) => ({
      date: date
    }));

    // Add the line first (so it appears behind the circles)
    svg.append('path')
      .datum(lineData)
      .attr('class', 'average-line')
      .attr('d', line)
      .attr('opacity', 0)
      .transition()
      .duration(500)
      .attr('opacity', 1);

    // Add average label
    const averageLabel = svg.append('text')
      .attr('class', 'average-label')
      .attr('x', width - margin.right - 100)
      .attr('y', y(averagePlatesPerDay) - 150)
      .attr('text-anchor', 'end')
      .text(`Average: ${Math.round(averagePlatesPerDay)} plates/day`)
      .attr('opacity', 0)
      .transition()
      .duration(500)
      .attr('opacity', 1);

    // Get the text width and position
    const labelWidth = averageLabel.node().getComputedTextLength();
    const labelX = width - margin.right - 100;
    const arrowX = labelX - (labelWidth / 2);

    // Add arrow from label to line
    svg.append('path')
      .attr('class', 'average-arrow')
      .attr('d', `M ${arrowX} ${y(averagePlatesPerDay) - 150} L ${arrowX} ${y(averagePlatesPerDay)}`)
      .attr('stroke', 'var(--faint-blue)')
      .attr('stroke-width', 1.5)
      .attr('marker-end', 'url(#arrowhead)')
      .attr('opacity', 0)
      .transition()
      .duration(500)
      .attr('opacity', 1);

    // Add arrowhead definition
    svg.append('defs').append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 8)
      .attr('refY', 0)
      .attr('orient', 'auto')
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', 'var(--faint-blue)');

    // select top plate for each date
    const topPlates = dateEntries.map(([date, plates]) => {
      // Find the plate with the most violations
      const plateWithMostViolations = plates.reduce((max, current) => 
        (current.violations > max.violations) ? current : max
      , plates[0]);
      
      return {
        ...plateWithMostViolations,
        n_plates: plates.length
      };
    });

    nodes = svg.selectAll('circle')
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
      .attr('opacity', CIRCLE_OPACITY)
      .attr('class', 'leaf-circle')
      .on('mouseover', function(event, d) {
        d3.select(this).classed("leaf-circle-hover", true);
          // Create or update tooltip
          const tooltip = d3.select(container)
            .selectAll(".tooltip")
            .data([null])
            .join("div")
            .attr("class", "tooltip");
          
          const tooltipContent = `
            <strong>Plate ID:</strong> ${d.plate}<br>
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
          d3.select(this).classed("leaf-circle-hover", false);
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

  onMount(async () => {
    // Load and process the data
    const response = await fetch('/data/plates_to_tow.csv');
    const csvText = await response.text();
    const parsedData = d3.csvParse(csvText);
    
    // Convert dates and filter for 2024, with error handling
    data = parsedData
      .filter(d => d && d.tow_eligible_date) // Filter out any null/undefined entries
      .map(d => ({
        ...d,
        tow_eligible_date: new Date(d.tow_eligible_date)
      }))
      .filter(d => !isNaN(d.tow_eligible_date.getTime())) // Filter out invalid dates
      .filter(d => d.tow_eligible_date.getFullYear() === 2024)
      .sort((a, b) => a.tow_eligible_date - b.tow_eligible_date);

    // Create visualization immediately
    createVisualization();
  });

  // Function to update visualization based on scroll section
  function updateVisualization(currentSection) {
    if (!svg || !data || data.length === 0) return;

    // Add different effects based on the current section
    if (currentSection === 0) {
      // Reset to full view
      const y = regenerateAxes(data);
      if (!y) return;
      
      // Remove the connecting line
      svg.selectAll('.connect-line')
        .transition()
        .duration(500)
        .attr('opacity', 0)
        .remove();
      
      // Update points - select the date groups and rebind data
      const dateGroups = d3.group(data, d => d.tow_eligible_date);
      const dateEntries = Array.from(dateGroups.entries());
      
       // Update opacity using the nodes object
       nodes
        .transition()
        .duration(500)
        .attr('cx', d => x(d.tow_eligible_date))
        .attr('cy', d => y(d.n_plates))
        .attr('opacity', CIRCLE_OPACITY);
      
      
      // Update line and label
      const totalPlates = data.length;
      const totalDays = dateEntries.length;
      const averagePlatesPerDay = totalPlates / totalDays;
      
      const line = d3.line()
        .x(d => x(d.date))
        .y(() => y(averagePlatesPerDay))
        .curve(d3.curveMonotoneX);

      // Update the average line
      svg.select('.average-line')
        .datum(dateEntries.map(([date]) => ({ date: date })))
        .transition()
        .duration(500)
        .attr('d', line);

      // Update the average label
      svg.select('.average-label')
        .transition()
        .duration(500)
        .attr('y', y(averagePlatesPerDay) - 150)
        .text(`Average: ${Math.round(averagePlatesPerDay)} plates/day`);
    }
    else if (currentSection === 1) {
      // Filter data for August 2024
      const augustData = data.filter(d => d.tow_eligible_date.getMonth() === 7 && d.tow_eligible_date.getFullYear() === 2024);
      const y = regenerateAxes(augustData, "%b %d");

      // Get August date groups
      const augustGroups = d3.group(augustData, d => d.tow_eligible_date);
      const augustEntries = Array.from(augustGroups.entries());
      
      // Create a line generator for connecting circles
      const connectLine = d3.line()
        .x(d => x(d.tow_eligible_date))
        .y(d => y(d.n_plates))
        .curve(d3.curveMonotoneX);

      // Add or update the connecting line
      svg.selectAll('.connect-line').remove(); // Remove existing line if any
      svg.append('path')
        .attr('class', 'connect-line')
        .datum(augustEntries.map(([date, plates]) => ({
          tow_eligible_date: date,
          n_plates: plates.length
        })))
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
        .attr('cx', d => x(d.tow_eligible_date))
        .attr('cy', d => y(d.n_plates))
        .attr('opacity', (d) => (d.tow_eligible_date.getMonth() === 7 && d.tow_eligible_date.getFullYear() === 2024) ? CIRCLE_OPACITY : 0);
      
      // Update average line for August
      const totalPlates = augustData.length;
      const totalDays = augustEntries.length;
      const averagePlatesPerDay = totalPlates / totalDays;
      

      const line = d3.line()
        .x(d => x(d.date))
        .y(() => y(averagePlatesPerDay))
        .curve(d3.curveMonotoneX);

      // Update the average line
      svg.select('.average-line')
        .datum(augustEntries.map(([date]) => ({ date: date })))
        .transition()
        .duration(500)
        .attr('d', line);

      // Update the average label
      svg.select('.average-label')
        .transition()
        .duration(500)
        .text(`Average: ${Math.round(averagePlatesPerDay)} plates/day in August`);
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
    fill: var(--primary-blue);
    stroke: none;
    stroke-width: 0;
  }
  
  :global(.leaf-circle-hover) {
    fill: var(--dark-blue);
    stroke-width: 0.5px;
    stroke: black;
  }

  :global(.axis-label) {
    font-family: Helvetica, Arial, sans-serif;
    font-weight: 300;
    font-size: 18px;
  }

  :global(.average-label) {
    font-family: Helvetica, Arial, sans-serif;
    font-weight: 400;
    font-size: 14px;
    z-index: 10000;
    fill: var(--faint-blue);
  }

  :global(.average-line) {
    stroke:  var(--faint-blue);
    stroke-width: 2;
    stroke-dasharray: 5, 5;
  }
</style>
