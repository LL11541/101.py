let binId = null;
let accessKey = null;
let particles = [];
let targetText = '';
let isConnected = false;
let isLoading = false;
let pollInterval = null;

const PARTICLE_SIZE = 8;
const ALIGNMENT_RADIUS = 50;
const COHESION_RADIUS = 100;
const SEPARATION_RADIUS = 30;
const MAX_SPEED = 2;
const MAX_FORCE = 0.1;

class Particle {
    constructor(x, y, char) {
        this.char = char;
        this.pos = createVector(x, y);
        this.vel = createVector(random(-1, 1), random(-1, 1));
        this.acc = createVector(0, 0);
        this.targetPos = createVector(x, y);
        this.size = PARTICLE_SIZE;
    }

    update() {
        this.alignment();
        this.cohesion();
        this.separation();
        this.seekTarget();

        this.vel.add(this.acc);
        this.vel.limit(MAX_SPEED);
        this.pos.add(this.vel);
        this.acc.mult(0);

        this.edges();
    }

    alignment() {
        let sum = createVector(0, 0);
        let count = 0;
        
        for (let other of particles) {
            let d = p5.Vector.dist(this.pos, other.pos);
            if (d > 0 && d < ALIGNMENT_RADIUS) {
                sum.add(other.vel);
                count++;
            }
        }
        
        if (count > 0) {
            sum.div(count);
            sum.setMag(MAX_SPEED);
            sum.sub(this.vel);
            sum.limit(MAX_FORCE);
            this.acc.add(sum.mult(0.5));
        }
    }

    cohesion() {
        let sum = createVector(0, 0);
        let count = 0;
        
        for (let other of particles) {
            let d = p5.Vector.dist(this.pos, other.pos);
            if (d > 0 && d < COHESION_RADIUS) {
                sum.add(other.pos);
                count++;
            }
        }
        
        if (count > 0) {
            sum.div(count);
            sum.sub(this.pos);
            sum.setMag(MAX_SPEED);
            sum.sub(this.vel);
            sum.limit(MAX_FORCE);
            this.acc.add(sum.mult(0.3));
        }
    }

    separation() {
        let sum = createVector(0, 0);
        let count = 0;
        
        for (let other of particles) {
            let d = p5.Vector.dist(this.pos, other.pos);
            if (d > 0 && d < SEPARATION_RADIUS) {
                let diff = p5.Vector.sub(this.pos, other.pos);
                diff.normalize();
                diff.div(d);
                sum.add(diff);
                count++;
            }
        }
        
        if (count > 0) {
            sum.div(count);
            sum.setMag(MAX_SPEED);
            sum.sub(this.vel);
            sum.limit(MAX_FORCE);
            this.acc.add(sum.mult(1.5));
        }
    }

    seekTarget() {
        let desired = p5.Vector.sub(this.targetPos, this.pos);
        let d = desired.mag();
        
        if (d > 0) {
            desired.normalize();
            desired.mult(MAX_SPEED);
            let steer = p5.Vector.sub(desired, this.vel);
            steer.limit(MAX_FORCE);
            this.acc.add(steer.mult(0.8));
        }
    }

    edges() {
        if (this.pos.x < 0) this.pos.x = width;
        if (this.pos.x > width) this.pos.x = 0;
        if (this.pos.y < 0) this.pos.y = height;
        if (this.pos.y > height) this.pos.y = 0;
    }

    show() {
        push();
        translate(this.pos.x, this.pos.y);
        rotate(this.vel.heading());
        
        fill(100, 200, 255, 200);
        noStroke();
        textSize(this.size);
        textAlign(CENTER, CENTER);
        text(this.char, 0, 0);
        pop();
    }
}

function setup() {
    let canvas = createCanvas(windowWidth, windowHeight);
    canvas.parent('canvas-container');
    textFont('Arial');
}

function draw() {
    background(10, 10, 15, 20);

    if (!isConnected) {
        fill(150);
        textSize(24);
        textAlign(CENTER, CENTER);
        text('请在上方输入 Bin ID 和 Access Key 后点击连接', width/2, height/2);
        return;
    }

    if (isLoading) {
        fill(150);
        textSize(20);
        textAlign(CENTER, CENTER);
        text('加载中...', width/2, height/2);
        return;
    }

    for (let p of particles) {
        p.update();
        p.show();
    }
}

function windowResized() {
    resizeCanvas(windowWidth, windowHeight);
    updateParticleTargets();
}

function startConnection() {
    binId = document.getElementById('binId').value.trim();
    accessKey = document.getElementById('accessKey').value.trim();
    
    if (!binId || !accessKey) {
        document.getElementById('status').textContent = '请填写 Bin ID 和 Access Key';
        document.getElementById('status').style.color = '#f44336';
        return;
    }
    
    isConnected = true;
    document.getElementById('status').textContent = '已连接，正在加载数据...';
    document.getElementById('status').style.color = '#4CAF50';
    
    loadData();
    
    if (pollInterval) {
        clearInterval(pollInterval);
    }
    pollInterval = setInterval(loadData, 3000);
}

async function loadData() {
    if (!isConnected || !binId || !accessKey || isLoading) return;
    
    isLoading = true;
    try {
        let response = await fetch(`https://api.jsonbin.io/v3/b/${binId}/latest`, {
            headers: {
                'X-Access-Key': accessKey
            }
        });
        
        if (response.ok) {
            let result = await response.json();
            let newText = result.record?.text || '';
            
            if (newText !== targetText) {
                targetText = newText;
                createParticles();
                document.getElementById('status').textContent = '连接成功 | 已更新';
                document.getElementById('status').style.color = '#4CAF50';
            }
        } else {
            document.getElementById('status').textContent = '加载失败: ' + response.status;
            document.getElementById('status').style.color = '#f44336';
        }
    } catch (error) {
        console.error('加载失败:', error);
        document.getElementById('status').textContent = '连接错误: ' + error.message;
        document.getElementById('status').style.color = '#f44336';
    }
    isLoading = false;
}

function createParticles() {
    particles = [];
    
    if (!targetText) {
        return;
    }
    
    let fontSize = 32;
    textSize(fontSize);
    textAlign(CENTER, BASELINE);
    
    let lines = targetText.split('\n');
    let yOffset = (lines.length - 1) * fontSize * 1.5;
    let startY = height / 2 - yOffset / 2;
    
    for (let i = 0; i < lines.length; i++) {
        let line = lines[i];
        let lineWidth = textWidth(line);
        let startX = (width - lineWidth) / 2;
        
        for (let j = 0; j < line.length; j++) {
            let char = line[j];
            if (char === ' ') continue;
            
            let charWidth = textWidth(char);
            let x = startX + j * charWidth + charWidth / 2;
            let y = startY + i * fontSize * 1.5;
            
            let particle = new Particle(
                random(width),
                random(height),
                char
            );
            particle.targetPos = createVector(x, y);
            particles.push(particle);
        }
    }
}

function updateParticleTargets() {
    if (!targetText) return;
    
    let fontSize = 32;
    textSize(fontSize);
    textAlign(CENTER, BASELINE);
    
    let lines = targetText.split('\n');
    let yOffset = (lines.length - 1) * fontSize * 1.5;
    let startY = height / 2 - yOffset / 2;
    
    let index = 0;
    for (let i = 0; i < lines.length; i++) {
        let line = lines[i];
        let lineWidth = textWidth(line);
        let startX = (width - lineWidth) / 2;
        
        for (let j = 0; j < line.length; j++) {
            let char = line[j];
            if (char === ' ') continue;
            
            if (index < particles.length) {
                let charWidth = textWidth(char);
                let x = startX + j * charWidth + charWidth / 2;
                let y = startY + i * fontSize * 1.5;
                particles[index].targetPos = createVector(x, y);
                index++;
            }
        }
    }
}
