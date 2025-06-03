<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';
  import Scrolly from "$lib/components/helpers/scrolly.svelte";
  import { getFullPath } from '$lib/utils/paths';

  // Props for the component
  let {
        dataPath = '/data/plates_to_tow.csv',
        width = 800,
        height = 500,
        CIRCLE_RADIUS = 5,
        CIRCLE_OPACITY = 0.8,
        sharePlatesMajorityViolationsPostTowEligible = .25,
        margin = { top: 20, right: 20, bottom: 100, left: 60 },
    } = $props();

  let topPlates;
  let svg;
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
      content: "Let's look at one specific vehicle in detail."
    }, 
    {
      title: "",
      content: "Let's look at one specific vehicle in detail."
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

    // Filter data for August 2024
    const augustData = data.filter(d => d.tow_eligible_date.getMonth() === 7 && d.tow_eligible_date.getFullYear() === 2024);
    
    // Add axes first with August-specific domain
    x = d3.scaleTime()
      .domain(d3.extent(augustData, d => d.tow_eligible_date))
      .range([margin.left, width - margin.right]);

    const augustGroups = d3.group(augustData, d => d.tow_eligible_date);
    const maxPlatesPerDate = d3.max(Array.from(augustGroups.values()), plates => plates.length);
    const roundedMax = Math.ceil(maxPlatesPerDate / 5) * 5;

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
      .text('Number of plates entering judgement');

    // Get all date groups for creating all nodes
    const dateGroups = d3.group(data, d => d.tow_eligible_date);
    const dateEntries = Array.from(dateGroups.entries());

    // select top plate for each date
    topPlates = dateEntries.map(([date, plates]) => {
      // First, find plates that meet our criteria
      const highPostViolationPlates = plates.filter(p => p.violations_post_tow_eligible > p.violations/2);
      
      // With set probability, select from high post-violation plates if any exist
      if (highPostViolationPlates.length > 0 && Math.random() < sharePlatesMajorityViolationsPostTowEligible) {
        // Randomly select one of the high post-violation plates
        const selectedPlate = highPostViolationPlates[Math.floor(Math.random() * highPostViolationPlates.length)];
        return {
          ...selectedPlate,
          n_plates: plates.length
        };
      }
      
      // Otherwise, find the plate with the most violations
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
            tow_eligible_date: new Date(d.tow_eligible_date)
          }))
          .filter(d => !isNaN(d.tow_eligible_date.getTime())) // Filter out invalid dates
          .filter(d => d.tow_eligible_date.getFullYear() === 2024)
          .sort((a, b) => a.tow_eligible_date - b.tow_eligible_date);
        
        // Create visualization immediately
        createVisualization();
      })
      .catch((error) => {
        console.error("Error loading CSV:", error);
      });
  });

  // Function to update visualization based on scroll section
  function updateVisualization(currentSection) {
    if (!svg || !data || data.length === 0) return;

    // Add different effects based on the current section
    if (currentSection === 0) {

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
        .attr('opacity', (d) => (d.tow_eligible_date.getMonth() === 7 && d.tow_eligible_date.getFullYear() === 2024) ? CIRCLE_OPACITY : 0)
        .attr('fill', 'var(--primary-blue)');
    }
      
    else if (currentSection === 1) {
      // Reset to full view
      const y = regenerateAxes(data);
      if (!y) return;
      
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
      const rollingAverageData = dateEntries.map(([date, plates], i) => {
        // Get the previous 90 days of data (or fewer if at the start)
        const startIdx = Math.max(0, i - 89);
        const windowData = dateEntries.slice(startIdx, i + 1);
        
        // Calculate average plates per day in the window
        const totalPlates = windowData.reduce((sum, [_, plates]) => sum + plates.length, 0);
        const avgPlates = totalPlates / windowData.length;
        
        return {
          tow_eligible_date: date,
          n_plates: avgPlates
        };
      });

      // Create a line generator for the rolling average
      const connectLine = d3.line()
        .x(d => x(d.tow_eligible_date))
        .y(d => y(d.n_plates))
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
        .attr('cx', d => x(d.tow_eligible_date))
        .attr('cy', d => y(d.n_plates))
        .attr('opacity', CIRCLE_OPACITY)
        .attr('fill', 'var(--primary-blue)');
    }

    if (currentSection === 2) {
      nodes.transition()
        .duration(500)
        .attr('fill', d => d.violations_post_tow_eligible > d.violations/2 ? 'var(--worst-offenders)' : 'var(--primary-blue)')
        .attr('opacity', CIRCLE_OPACITY);
    }

    if (currentSection === 3) {

      // Hide axes and labels
      svg.selectAll('.x-axis, .y-axis, .axis-label')
        .transition()
        .duration(500)
        .attr('opacity', 0);

      svg.selectAll('.connect-line').remove(); // Remove existing line if any


      // Define spiral boundaries
      const binWidth = width / 3; // Width of each bin
      const binHeight = height / 2; // Height of each bin
      const leftBinX = width / 4; // Center of left bin
      const rightBinX = 3 * width / 4; // Center of right bin
      const binY = height / 2; // Center of bins vertically
      // Use a constant gap of 2px between each node along the spiral
      const gap = 10; // px between each node
      const b = 6; // spiral tightness, adjust for visual preference

      nodes
        .transition()
        .duration(500)
        .attr('cx', d => {
          const isRightSide = d.violations_post_tow_eligible > (d.violations) / 2;
          const sameGroupNodes = Array.from(nodes.filter(n => 
            (n.violations_post_tow_eligible > (n.violations) / 2) === isRightSide
          ).data());
          const groupIndex = sameGroupNodes.indexOf(d);

          // Constant-gap spiral calculation
          let theta = 0;
          let r = 0;
          for (let i = 0; i < groupIndex; i++) {
            // r = b * theta
            // dr/dtheta = b
            // ds = sqrt(r^2 + (dr/dtheta)^2) dtheta
            // dtheta = gap / sqrt(r^2 + b^2)
            const dtheta = gap / Math.sqrt(r * r + b * b);
            theta += dtheta;
            r = b * theta;
          }
          const spiralX = Math.cos(theta) * r;
          // Position in appropriate bin, mirror the right side
          return isRightSide ? rightBinX - spiralX : leftBinX + spiralX;
        })
        .attr('cy', d => {
          const isRightSide = d.violations_post_tow_eligible > (d.violations) / 2;
          const sameGroupNodes = Array.from(nodes.filter(n => 
            (n.violations_post_tow_eligible > (n.violations) / 2) === isRightSide
          ).data());
          const groupIndex = sameGroupNodes.indexOf(d);

          // Constant-gap spiral calculation
          let theta = 0;
          let r = 0;
          for (let i = 0; i < groupIndex; i++) {
            const dtheta = gap / Math.sqrt(r * r + b * b);
            theta += dtheta;
            r = b * theta;
          }
          const spiralY = Math.sin(theta) * r;
          // Position in appropriate bin
          return binY + spiralY;
        })
        .attr('r', CIRCLE_RADIUS)
        .attr('opacity', CIRCLE_OPACITY);

      // Add labels for the stacks
      svg.selectAll('.stack-label').remove();
      
      svg.append('text')
        .attr('class', 'stack-label')
        .attr('x', leftBinX)
        .attr('y', binY - 220)
        .attr('text-anchor', 'middle')
        .text('Plates who mostly violate')
        .attr('opacity', 0)
        .transition()
        .duration(500)
        .attr('opacity', 1);

        svg.append('text')
        .attr('class', 'stack-label')
        .attr('x', rightBinX)
        .attr('y', binY - 220)
        .attr('text-anchor', 'middle')
        .text('Plates who mostly violate')
        .attr('opacity', 0)
        .transition()
        .duration(500)
        .attr('opacity', 1);

      svg.append('text')
        .attr('class', 'stack-label')
        .attr('x', leftBinX)
        .attr('y', binY - 200)
        .attr('text-anchor', 'middle')
        .text(`before entering judgement (${(1 - sharePlatesMajorityViolationsPostTowEligible) * 100}%)`)
        .attr('opacity', 0)
        .transition()
        .duration(500)
        .attr('opacity', 1);

      svg.append('text')
        .attr('class', 'stack-label')
        .attr('x', rightBinX)
        .attr('y', binY - 200)
        .attr('text-anchor', 'middle')
        .text(`after entering judgement (${sharePlatesMajorityViolationsPostTowEligible * 100}%)`)
        .attr('opacity', 0)
        .transition()
        .duration(500)
        .attr('opacity', 1);
    }
    
    if (currentSection === 4) {
      // Hide axes and labels
      svg.selectAll('.x-axis, .y-axis, .axis-label')
        .transition()
        .duration(500)
        .attr('opacity', 0);

      svg.selectAll('.stack-label').remove(); // Remove existing line if any

      // Select a random plate
      const randomIndex = Math.floor(Math.random() * topPlates.length);
      const targetNode = topPlates[randomIndex];
      console.log(`Selected random plate: ${targetNode.plate}`);
      if (!targetNode) return;

      // Calculate zoom parameters
      const zoomRadius = Math.min(width, height) * 0.5; // 40% of the smaller screen dimension
      const centerX = width / 2;
      const centerY = height / 2;

      // Update all nodes
      nodes
        .transition()
        .duration(1000)
        .attr('cx', d => {
          if (d.plate === targetNode.plate) {
            return centerX;
          }
          // Move other nodes to the edges
          const isRightSide = d.violations_post_tow_eligible > (d.violations) / 2;
          return isRightSide ? width - 50 : 50;
        })
        .attr('cy', d => {
          if (d.plate === targetNode.plate) {
            return centerY;
          }
          // Distribute other nodes vertically
          const index = topPlates.indexOf(d);
          return (index % 2 === 0) ? 50 : height - 50;
        })
        .attr('r', d => d.plate === targetNode.plate ? zoomRadius : CIRCLE_RADIUS)
        .attr('opacity', d => d.plate === targetNode.plate ? CIRCLE_OPACITY : 0)
        .attr('mouseover', null);

      // Add detailed label for the target node
      svg.selectAll('.node-label').remove();
      svg.append('text')
        .attr('class', 'node-label')
        .attr('x', centerX)
        .attr('y', centerY - zoomRadius - 20)
        .attr('text-anchor', 'middle')
        .text(`Plate: ${targetNode.plate}`)
        .attr('opacity', 0)
        .transition()
        .duration(500)
        .attr('opacity', 1);

      svg.append('text')
        .attr('class', 'node-label')
        .attr('x', centerX)
        .attr('y', centerY - zoomRadius - 40)
        .attr('text-anchor', 'middle')
        .text(`Total Violations: ${targetNode.violations}`)
        .attr('opacity', 0)
        .transition()
        .duration(500)
        .attr('opacity', 1);

      svg.append('text')
        .attr('class', 'node-label')
        .attr('x', centerX)
        .attr('y', centerY - zoomRadius - 60)
        .attr('text-anchor', 'middle')
        .text(`Post-Tow Violations: ${targetNode.violations_post_tow_eligible}`)
        .attr('opacity', 0)
        .transition()
        .duration(500)
        .attr('opacity', 1);
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
    font-size: 18px;
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
</style>
