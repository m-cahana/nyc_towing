<script>
    import Footer from "$lib/components/footer.svelte";
    import Barplot from "$lib/components/barplot.svelte";
    import TowPlates from "$lib/components/tow_plates.svelte";

    import { onMount } from 'svelte';

    onMount(() => {
        window.scrollTo(0, 0);
    });
</script>

<main>
	<h1>Tens of Thousands of Recidivist Speeders Evaded The Law in 2024</h1>
    <div class="subtitle">June 2025</div>

    <p>
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
    </p>

    <Barplot />

    <p>
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
    </p>

    <TowPlates />

    <p>
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
    </p>

    <Footer />
</main>


<style>
	main {
		margin: 0 auto;
		max-width: 800px;
		padding: 1rem;
        font-family: "Helvetica";
		text-align: center;
	}


	h1 {
		font-size: 36px;
        font-style: italic;
        font-weight: 300;
        margin-bottom: 0.2rem;
	}

    p {
        font-size: 16px;
        text-align: left;
        font-weight: 300;
    }

    .subtitle {
        font-size: 20px;
        font-style: italic;
        font-weight: 300;
        margin-top: 0;
    }
</style>