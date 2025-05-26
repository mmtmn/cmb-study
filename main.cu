// nvcc -o main main.cu -lGL -lGLU -lglfw -lGLEW -ldl

#include <GL/glew.h>
#include <GLFW/glfw3.h>
#include <iostream>
#include <fstream>
#include <vector>
#include <cmath>
#include <cassert>

#define WIDTH  1200
#define HEIGHT 900

GLuint vbo, vao;
size_t pointCount = 0;

// === Camera control ===
float yaw = 0.0f, pitch = 0.0f;
float zoom = 3.5f;
double lastX, lastY;
bool rotating = false, panning = false;
float panX = 0.0f, panY = 0.0f;

// === Raw .npy loader (no numpy headers) ===
void loadNpy(const char* filename, std::vector<float>& data) {
    FILE* f = fopen(filename, "rb");
    if (!f) {
        std::cerr << "Could not open " << filename << std::endl;
        exit(1);
    }

    // --- Skip .npy header ---
    char header[256];
    fread(header, 1, 256, f);

    long pos = ftell(f);
    while (pos < 512) {
        if (header[pos] == '\n') break;
        pos++;
    }
    fseek(f, pos + 1, SEEK_SET);  // Go to start of binary data

    // --- Read data ---
    fseek(f, 0, SEEK_END);
    long file_size = ftell(f);
    long data_offset = pos + 1;
    long data_size = file_size - data_offset;
    long count = data_size / sizeof(float);

    fseek(f, data_offset, SEEK_SET);
    data.resize(count);
    fread(data.data(), sizeof(float), count, f);
    fclose(f);

    pointCount = count / 6;
    std::cout << "Loaded " << pointCount << " points from " << filename << std::endl;
}

// === OpenGL setup ===
void setupGL(const std::vector<float>& data) {
    glEnable(GL_DEPTH_TEST);
    glEnable(GL_PROGRAM_POINT_SIZE);
    glPointSize(1.0f);

    glGenVertexArrays(1, &vao);
    glBindVertexArray(vao);

    glGenBuffers(1, &vbo);
    glBindBuffer(GL_ARRAY_BUFFER, vbo);
    glBufferData(GL_ARRAY_BUFFER, data.size() * sizeof(float), data.data(), GL_STATIC_DRAW);

    glEnableVertexAttribArray(0); // Position
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void*)0);

    glEnableVertexAttribArray(1); // Color
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void*)(3 * sizeof(float)));
}

// === Rendering ===
void draw() {
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glLoadIdentity();
    glTranslatef(panX, panY, -zoom);
    glRotatef(pitch, 1.0f, 0.0f, 0.0f);
    glRotatef(yaw, 0.0f, 1.0f, 0.0f);
    glBindVertexArray(vao);
    glDrawArrays(GL_POINTS, 0, pointCount);
}

// === Input callbacks ===
void cursor_callback(GLFWwindow* window, double xpos, double ypos) {
    static double lastX = xpos, lastY = ypos;
    double dx = xpos - lastX;
    double dy = ypos - lastY;
    lastX = xpos;
    lastY = ypos;

    if (rotating) {
        yaw += dx * 0.2f;
        pitch += dy * 0.2f;
    }
    if (panning) {
        panX += dx * 0.005f;
        panY -= dy * 0.005f;
    }
}

void mouse_button_callback(GLFWwindow* window, int button, int action, int mods) {
    if (button == GLFW_MOUSE_BUTTON_LEFT)
        rotating = (action == GLFW_PRESS);
    if (button == GLFW_MOUSE_BUTTON_RIGHT)
        panning = (action == GLFW_PRESS);
}

void scroll_callback(GLFWwindow* window, double xoffset, double yoffset) {
    zoom -= yoffset * 0.2f;
    if (zoom < 0.1f) zoom = 0.1f;
}

// === Main ===
int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Usage: ./hologram_cuda full_cloud.npy" << std::endl;
        return 1;
    }

    if (!glfwInit()) {
        std::cerr << "Failed to init GLFW" << std::endl;
        return -1;
    }

    GLFWwindow* window = glfwCreateWindow(WIDTH, HEIGHT, "Holographic CMB Viewer", nullptr, nullptr);
    if (!window) return -1;

    glfwMakeContextCurrent(window);
    glewInit();

    // Load point cloud
    std::vector<float> data;
    loadNpy(argv[1], data);
    setupGL(data);

    // Set input callbacks
    glfwSetCursorPosCallback(window, cursor_callback);
    glfwSetMouseButtonCallback(window, mouse_button_callback);
    glfwSetScrollCallback(window, scroll_callback);

    // Main render loop
    while (!glfwWindowShouldClose(window)) {
        draw();
        glfwSwapBuffers(window);
        glfwPollEvents();
    }

    glfwTerminate();
    return 0;
}
