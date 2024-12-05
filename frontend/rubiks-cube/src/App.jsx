import { useEffect, useState, useRef } from 'react';
import { GUI } from 'dat.gui';
import * as THREE from 'three';
import SceneInit from './lib/SceneInit';
import RubiksCube from './lib/RubiksCube';

function App() {
  // Define the RubiksCube instance outside of useEffect
  let r= useRef(null);

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
      const response = await sendScrambleToAPI(scrambleMoves); // Replace with your API URL
      const data_idx = response;
      console.log('Data_idx:', data_idx);
      console.log('API Response:', data_idx); // Log the response data
      const data = [];
      console.log('Data_idx:', data_idx);
      for (const idx of data_idx) {
        console.log(moves[idx]);
        data.push(moves[idx][0]); 
        data.push(moves[idx][1]);
      }
      // console.log('Moves:', data);
      await executeMoves(data);
    } catch (error) {
      console.error('Error fetching moves:', error.message);
    }
     // Assuming the response has a 'moves' array
    
  };

  // Function to execute moves on the Rubik's Cube
  const executeMoves = async (moves) => {

    if (Array.isArray(moves)) {
      for (const move of moves) {
        // Highlight cells based on the move
        console.log('Move:', move, r);
        r.current.highlightCells(move); // Now r is defined and accessible
        r.current.onKeyDown(move);
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
    const scrambleLength = 7; // Number of moves in the scramble

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

    r.current = new RubiksCube(); // Assign the RubiksCube instance to r
    test.scene.add(r.current.rubiksCubeGroup);

    const mouse = new THREE.Vector2();
    const raycaster = new THREE.Raycaster();

    function onMouseDown(event) {
      mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
      mouse.y = -(event .clientY / window.innerHeight) * 2 + 1;
      raycaster.setFromCamera(mouse, test.camera);
      const objects = raycaster.intersectObjects(r.current.rubiksCubeGroup.children);
      const cubeObjects = objects.filter((c) => {
        return c.object.type === 'Mesh';
      });
      if (cubeObjects.length > 0) {
        r.current.highlightCubes(cubeObjects[0].object);
      }
    }

    const onKeyDown = (event) => {
      if (event.repeat) {
        return;
      }
      r.current.onKeyDown(event);
    };

    window.addEventListener('keydown', onKeyDown);
    window.addEventListener('mousedown', onMouseDown);

    const gui = new GUI();
    const folder = gui.addFolder("Rubik's Cube");
    folder.add(r.current, 'epsilon', 0.5, 3.5, 0.5);
    folder.add(r.current, 'consoleDebug');
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