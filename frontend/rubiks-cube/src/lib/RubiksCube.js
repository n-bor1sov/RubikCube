import * as THREE from 'three';
import * as TWEEN from '@tweenjs/tween.js';

import Cube from './Cube';

export default class RubiksCube {
  constructor() {
    this.scale = 20;
    this.epsilon = 0.5;
    this.consoleDebug = true;
    this.selectedCube = null;
    this.rubiksCubeGroup = new THREE.Group();
    this.rubiksCubeGroup.scale.x = this.scale;
    this.rubiksCubeGroup.scale.y = this.scale;
    this.rubiksCubeGroup.scale.z = this.scale;

    this.rubiksCubeGroup.rotation.x = Math.PI / 7;
    this.rubiksCubeGroup.rotation.y = -Math.PI / 4;
    this.f_face = null;
    this.b_face = null;
    this.u_face = null;
    this.d_face = null;
    this.l_face = null;
    this.r_face = null;
    this.initializeRubiksCube();

    const anim = (t) => {
      TWEEN.update(t);
      requestAnimationFrame(anim);
    };
    anim();
  }

  rotateAroundWorldAxis(cubeGroup, axis) {
    const start = { rotation: 0 };
    const prev = { rotation: 0 };
    const end = { rotation: Math.PI / 2 };

    const tween = new TWEEN.Tween(start)
      .to(end, 500)
      .easing(TWEEN.Easing.Quadratic.InOut)
      .onUpdate(({ rotation }) => {
        // NOTE: Comment out each block to see different mistakes.

        // === 1 ===
        // cubeGroup.position.applyAxisAngle(axis, rotation - prev.rotation);

        // === 2 ===
        // cubeGroup.rotateOnWorldAxis(axis, rotation - prev.rotation);

        // === 3 ===
        // NOTE: DO NOT rotate the cube on it's own axis.
        // cubeGroup.position.applyAxisAngle(axis, rotation - prev.rotation);
        // cubeGroup.rotateOnAxis(axis, rotation - prev.rotation);

        // === 4 ===
        // NOTE: THIS IS CORRECT.
        // NOTE: Move the position of a cube.
        // NOTE: Rotate the cube on the world axis.
        cubeGroup.position.applyAxisAngle(axis, rotation - prev.rotation);
        cubeGroup.rotateOnWorldAxis(axis, rotation - prev.rotation);

        // NOTE: Keep track of the previous rotation for tweening.
        prev.rotation = rotation;
      });

    tween.start();
  }

  highlightCells(command) {
    // Reset all cubes to full opacity
    this.cubes.forEach((cube) => {
      cube.uniforms.opacity.value = 1.0;
    });
  
    // Highlight only the central cell based on the command
    switch (command) {
      case 'u_face': // Highlight top center cell
        this.cubes.forEach((cube) => {
          if (this.u_face == null){
            if (cube.cubeGroup.position.y === 1 && cube.cubeGroup.position.x === 0 && cube.cubeGroup.position.z === 0) {
              // cube.uniforms.opacity.value = 0.5;
              // this.selectedCube = cube; // Change opacity to highlight
              this.highlightCubes(cube.cubeMesh);
              this.u_face = cube.cubeMesh;
            }
          }
          else {
            this.highlightCubes(this.u_face);
          }
        });
        break;
      case 'd_face': // Highlight bottom center cell
        this.cubes.forEach((cube) => {
          if (this.d_face == null){
          if (cube.cubeGroup.position.y === -1 && cube.cubeGroup.position.x === 0 && cube.cubeGroup.position.z === 0) {
            // cube.uniforms.opacity.value = 0.5;
            // this.selectedCube = cube; // Change opacity to highlight
            this.highlightCubes(cube.cubeMesh);
            this.d_face = cube.cubeMesh;
          }
        }
        else {
          this.highlightCubes(this.d_face);
        }
        });
        break;
      case 'l_face': // Highlight left center cell
        this.cubes.forEach((cube) => {
          if (this.l_face == null){
          if (cube.cubeGroup.position.x === -1 && cube.cubeGroup.position.y === 0 && cube.cubeGroup.position.z === 0) {
            // cube.uniforms.opacity.value = 0.5;
            // this.selectedCube = cube; // Change opacity to highlight
            this.highlightCubes(cube.cubeMesh);
            this.l_face = cube.cubeMesh;
          }
        }
        else {
          this.highlightCubes(this.l_face);
        }
        });
        break;
      case 'r_face': // Highlight right center cell
        this.cubes.forEach((cube) => {
          if (this.r_face == null){
          if (cube.cubeGroup.position.x === 1 && cube.cubeGroup.position.y === 0 && cube.cubeGroup.position.z === 0) {
            // cube.uniforms.opacity.value = 0.5;
            // this.selectedCube = cube; // Change opacity to highlight
            this.highlightCubes(cube.cubeMesh);
            this.r_face = cube.cubeMesh;
          }
        }
        else {
          this.highlightCubes(this.r_face);
        }
        });
        break;
      case 'f_face': // Highlight front center cell
        this.cubes.forEach((cube) => {
          if (this.f_face == null){
          if (cube.cubeGroup.position.z === 1 && cube.cubeGroup.position.y === 0 && cube.cubeGroup.position.x === 0) {
            // cube.uniforms.opacity.value = 0.5;
            // this.selectedCube = cube; // Change opacity to highlight
            this.highlightCubes(cube.cubeMesh);
            this.f_face = cube.cubeMesh;
          }
        }
        else {
          this.highlightCubes(this.f_face);
        }
        });
        break;
      case 'b_face': // Highlight back center cell
        this.cubes.forEach((cube) => {
          if (this.b_face == null){
          if (cube.cubeGroup.position.z === -1 && cube.cubeGroup.position.y === 0 && cube.cubeGroup.position.x === 0) {
            // cube.uniforms.opacity.value = 0.5;
            // this.selectedCube = cube; // Change opacity to highlight
            this.highlightCubes(cube.cubeMesh);
            this.b_face = cube.cubeMesh;
          }
        }
        else {
          this.highlightCubes(this.b_face);
        }
        });
        break;
      default:
        console.warn('Unknown command:', command);
    }
  }

  cubeInSameY(c1, c2) {
    return (
      c1.cubeGroup.position.y > c2.cubeGroup.position.y - this.epsilon &&
      c1.cubeGroup.position.y < c2.cubeGroup.position.y + this.epsilon
    );
  }

  cubeInSameX(c1, c2) {
    return (
      c1.cubeGroup.position.x > c2.cubeGroup.position.x - this.epsilon &&
      c1.cubeGroup.position.x < c2.cubeGroup.position.x + this.epsilon
    );
  }

  cubeInSameZ(c1, c2) {
    return (
      c1.cubeGroup.position.z > c2.cubeGroup.position.z - this.epsilon &&
      c1.cubeGroup.position.z < c2.cubeGroup.position.z + this.epsilon
    );
  }

  getText(key) {
    return (
      // {
      //   u: 'U move',
      //   z: 'Uc move',
      //   f: 'F move',
      //   x: 'Fc move',
      //   b: 'B move',
      //   c: 'Bc move',
      //   l: 'L move',
      //   v: 'Lc move',
      //   r: 'R move',
      //   n: 'Rc move',
      //   d: 'D move',
      //   m: 'Dc move'
      // }[key] || ''
      {
        w: 'W: rotate up',
        s: 'S: rotate down',
        a: 'A: rotate left',
        d: 'D: rotate right',
        q: 'Q: rotate face left',
        e: 'E: rotate face right',
      }[key] || ''
    );
  }

  displayKey(key) {
    if (this.consoleDebug) {
      console.log(
        `%c ${this.getText(key)} `,
        'background: #fafafa; color: #0a0a0a; font-size: 20px'
      );
    }
  }

  onKeyDown(event) {
    if (event.key === 'w' || event === 'w') {
      this.displayKey(event.key);
      const axis = new THREE.Vector3(-1, 0, 0);
      this.cubes.forEach((cube) => {
        if (this.cubeInSameX(cube, this.selectedCube)) {
          this.rotateAroundWorldAxis(cube.cubeGroup, axis);
        }
      });
    } else if (event.key === 'a' || event === 'a') {
      this.displayKey(event.key);
      const axis = new THREE.Vector3(0, -1, 0);
      this.cubes.forEach((cube) => {
        if (this.cubeInSameY(cube, this.selectedCube))
          this.rotateAroundWorldAxis(cube.cubeGroup, axis);
      });
    } else if (event.key === 's' || event === 's') {
      this.displayKey(event.key);
      const axis = new THREE.Vector3(1, 0, 0);
      this.cubes.forEach((cube) => {
        if (this.cubeInSameX(cube, this.selectedCube))
          this.rotateAroundWorldAxis(cube.cubeGroup, axis);
      });
    } else if (event.key === 'd' || event === 'd') {
      this.displayKey(event.key);
      const axis = new THREE.Vector3(0, 1, 0);
      this.cubes.forEach((cube) => {
        if (this.cubeInSameY(cube, this.selectedCube))
          this.rotateAroundWorldAxis(cube.cubeGroup, axis);
      });
    } else if (event.key === 'q' || event === 'q') {
      this.displayKey(event.key);
      const axis = new THREE.Vector3(0, 0, 1);
      this.cubes.forEach((cube) => {
        if (this.cubeInSameZ(cube, this.selectedCube))
          this.rotateAroundWorldAxis(cube.cubeGroup, axis);
      });
    } else if (event.key === 'e' || event === 'e') {
      this.displayKey(event.key);
      const axis = new THREE.Vector3(0, 0, -1);
      this.cubes.forEach((cube) => {
        if (this.cubeInSameZ(cube, this.selectedCube))
          this.rotateAroundWorldAxis(cube.cubeGroup, axis);
      });
    }
  }

  highlightCubes(cubeToHighlight) {
    this.cubes.forEach((cube) => {
      if (cube.cubeMesh.uuid === cubeToHighlight.uuid) {
        this.selectedCube = cube; // Store the highlighted cube
        cube.uniforms.opacity.value = 0.5; // Highlight the selected cube
      } else {
        cube.uniforms.opacity.value = 1.0; // Reset opacity for others
      }
    });
  }

  initializeRubiksCube() {
    this.cubes = [
      // Front 2x2.
      // new Cube(-1, 1, 1),
      // new Cube(1, 1, 1),
      // new Cube(-1, -1, 1),
      // new Cube(1, -1, 1),

      // Back 2x2.
      // new Cube(-1, 1, -1),
      // new Cube(1, 1, -1),
      // new Cube(-1, -1, -1),
      // new Cube(1, -1, -1),

      // Front face.
      new Cube(-1, 1, 1),
      new Cube(0, 1, 1),
      new Cube(1, 1, 1),
      new Cube(-1, 0, 1),
      new Cube(0, 0, 1),
      new Cube(1, 0, 1),
      new Cube(-1, -1, 1),
      new Cube(0, -1, 1),
      new Cube(1, -1, 1),

      // Middle face.
      new Cube(-1, 1, 0),
      new Cube(0, 1, 0),
      new Cube(1, 1, 0),
      new Cube(-1, 0, 0),
      new Cube(0, 0, 0),
      new Cube(1, 0, 0),
      new Cube(-1, -1, 0),
      new Cube(0, -1, 0),
      new Cube(1, -1, 0),

      // Back face.
      new Cube(-1, 1, -1),
      new Cube(0, 1, -1),
      new Cube(1, 1, -1),
      new Cube(-1, 0, -1),
      new Cube(0, 0, -1),
      new Cube(1, 0, -1),
      new Cube(-1, -1, -1),
      new Cube(0, -1, -1),
      new Cube(1, -1, -1),
    ];

    this.cubes.forEach((cube) => {
      this.rubiksCubeGroup.add(cube.cubeGroup);
    });

    this.selectedCube = this.cubes[0];
  }
}
