import { useEffect, useState } from 'react';
import { GUI } from 'dat.gui';
import * as THREE from 'three';
import SceneInit from './lib/SceneInit';
import RubiksCube from './lib/RubiksCube';

function App() {
  // Define the RubiksCube instance outside of useEffect
  let r;

  // State to hold the list of moves
  const [scrambleMoves, setScrambleMoves] = useState([]);
  const moves = [['u_face', 'a'], ['u_face', 'd'],
                   ['f_face', 'e'], ['f_face', 'q'],
                   ['l_face', 's'], ['l_face', 'w'],
                   ['r_face', 'w'], ['r_face', 's'],
                   ['b_face', 'q'], ['b_face', 'e'],
                   ['d_face', 'd'], ['d_face', 'a']];

  // Define fetchMoves function here
  const fetchMoves = async () => {
    try {
      const response = sendScrambleToAPI(scrambleMoves); // Replace with your API URL
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data_idx = await response.json();
      console.log('API Response:', data_idx); // Log the response data
      const data = [];
      for (const idx of data_idx) {
        data.push(moves[idx]);
      }
      await executeMoves(data); // Assuming the response has a 'moves' array
    } catch (error) {
      console.error('Error fetching moves:', error.message);
    }
  };

  // Function to execute moves on the Rubik's Cube
  const executeMoves = async (moves) => {
    if (Array.isArray(moves)) {
      for (const move of moves) {
        // Highlight cells based on the move
        r.highlightCells(move); // Now r is defined and accessible
        r.onKeyDown(move);
        // Optionally, you can wait for a short duration to see the highlight effect
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    } else {
      console.error('Expected moves to be an array, but got:', moves);
    }
  };

  // Function to generate a random scramble
  const generateScramble = async () => {
    const scramble = [];
    const scrambleIdx = [];
    const scrambleLength = 5; // Number of moves in the scramble

    for (let i = 0; i < scrambleLength; i++) {
      let rnd_idx = Math.floor(Math.random() * moves.length);
      scramble.push(moves[rnd_idx][0]);
      scramble.push(moves[rnd_idx][1]);
      scrambleIdx.push(rnd_idx);
      console.log(moves[rnd_idx]);
    }

    setScrambleMoves(scrambleIdx); // Save the scramble to state
    console.log('Generated Scramble:', scramble); // Log the scramble

    // Execute the scramble moves on the Rubik's Cube
    await executeMoves(scramble);
  };

  // Function to send the scramble to the API
  const sendScrambleToAPI = async (scramble) => {
    try {
      const response = await fetch('http://127.0.0.1:5000/solve', { // Replace with your API URL
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ moves: scramble }), // Send the scramble as JSON
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Scramble sent to API:', data); // Log the response from the API
      return data;
    } catch (error) {
      console.error('Error sending scramble to API:', error.message);
    }
  };

  useEffect(() => {
    const test = new SceneInit('myThreeJsCanvas');
    test.initScene();
    test.animate();

    r = new RubiksCube(); // Assign the RubiksCube instance to r
    test.scene.add(r.rubiksCubeGroup);

    const mouse = new THREE.Vector2();
    const raycaster = new THREE.Raycaster();

    function onMouseDown(event) {
      mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
      mouse.y = -(event .clientY / window.innerHeight) * 2 + 1;
      raycaster.setFromCamera(mouse, test.camera);
      const objects = raycaster.intersectObjects(r.rubiksCubeGroup.children);
      const cubeObjects = objects.filter((c) => {
        return c.object.type === 'Mesh';
      });
      if (cubeObjects.length > 0) {
        r.highlightCubes(cubeObjects[0].object);
      }
    }

    const onKeyDown = (event) => {
      if (event.repeat) {
        return;
      }
      r.onKeyDown(event);
    };

    window.addEventListener('keydown', onKeyDown);
    window.addEventListener('mousedown', onMouseDown);

    const gui = new GUI();
    const folder = gui.addFolder("Rubik's Cube");
    folder.add(r, 'epsilon', 0.5, 3.5, 0.5);
    folder.add(r, 'consoleDebug');
    folder.open();

    // You can call fetchMoves here if you want to fetch moves on component mount
    //fetchMoves();

  }, []);

  return (
    <div>
      <canvas id="myThreeJsCanvas"></canvas>
      <button onClick={fetchMoves}>Fetch Moves</button> {/* Button to trigger fetching moves */}
      <button onClick={generateScramble} style={{ marginTop: '20px' }}>Scramble</button> {/* Button to trigger scramble */}
    </div>
  );
}

export default App;