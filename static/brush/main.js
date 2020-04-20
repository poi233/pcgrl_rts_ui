function run(canvas, obj, canClick) {
    obj = obj || {};
    this.canvas = canvas;
    this.cvs = canvas.getContext("2d");
    this.bgColor = obj.bgColor || "#e8e8e8";
    this.clickedColor = obj.clickedColor || "#ff0000";
    this.boxSize = obj.boxSize || 30;
    this.bgWidthLength = 8;
    this.bgHeightLength = 8;
    this.clickedArr = [];
    this.currentBrush = 2;
    this.start(this.bgWidthLength);
    if (canClick) {
        this.click();
    }
    return this;
}

run.prototype.start = function (size) {
    this.bgWidthLength = size;
    this.bgHeightLength = size;
    this.drawBg()
};

run.prototype.click = function () {

    let move = this.mousemove.bind(this);
    this.canvas.addEventListener("mousedown", function (e) {

        let o = this.computedXY(e.offsetX, e.offsetY);
        this.toggleClick(o);
        this.canvas.addEventListener("mousemove", move);

    }.bind(this));

    this.canvas.addEventListener("mouseup", function (e) {
        this.canvas.removeEventListener("mousemove", move);
    }.bind(this))
};

run.prototype.mousemove = function (e) {
    let o = this.computedXY(e.offsetX, e.offsetY);
    this.toggleClick(o, true);
};

run.prototype.changeClickColor = function (color) {
    this.clickedColor = color;
};

run.prototype.computedXY = function (x, y) {

    for (let i = 0; i < this.bgWidthLength; i++) {
        if (x > i * this.boxSize && x < (i + 1) * this.boxSize) {
            x = i;
            break;
        }
    }
    for (let i = 0; i < this.bgHeightLength; i++) {
        if (y > i * this.boxSize && y < (i + 1) * this.boxSize) {
            y = i;
            break;
        }
    }

    return {
        x,
        y
    }
};

run.prototype.toggleClick = function (o, draw) {
    let has = {};
    has.is = true;

    this.clickedArr.forEach(function (item, index) {

        if (item["point"].x === o.x && item["point"].y === o.y) {
            has.is = false;
            has.index = index;
        }
    });

    if (has.is) {
        if (o.x >= this.bgHeightLength || o.y >= this.bgHeightLength) {
            return;
        }
        this.clickedArr.push({"point": o, "type": this.currentBrush});
        this.drawBgBox(o.x * this.boxSize, o.y * this.boxSize, true);
    }
    if (!has.is && !draw) {
        this.clickedArr.splice(has.index, 1);
        this.drawBgBox(o.x * this.boxSize, o.y * this.boxSize);
    }

};

run.prototype.draw = function (initMap) {
    for (let i = 0; i < initMap.length; i++) {
        for (let j = 0; j < initMap[0].length; j++) {
            if (initMap[i][j] !== 0) {
                let item = initMap[i][j]
                if (item === 1) {
                    this.changeClickColor("#00ff00")
                } else if (item === 2) {
                    this.changeClickColor("#0000ff")
                } else if (item === 3) {
                    this.changeClickColor("#ff0000")
                }
                this.drawBgBox(i * this.boxSize, j * this.boxSize, true);
            }
        }
    }
};

run.prototype.Random = function (length) {

    for (let i = 0; i < length; i++) {
        let o = {};
        o.x = parseInt(Math.random() * this.bgWidthLength);
        o.y = parseInt(Math.random() * this.bgHeightLength);
        o.type = this.currentBrush;
        this.toggleClick(o);
    }
};

run.prototype.showRes = function () {
    let heatMap = [];
    for (let i = 0; i < this.bgWidthLength; i++) {
        let row = [];
        for (let j = 0; j < this.bgHeightLength; j++) {
            row.push(0)
        }
        heatMap.push(row)
    }
    let res = "";
    for (let i = 0; i < this.clickedArr.length; i++) {
        o = this.clickedArr[i];
        res += o["point"].x + "," + o["point"].y + "," + o["type"] + "|";
    }
    return res;
};

run.prototype.clean = function () {

    this.clickedArr.forEach(function (o, index) {
        this.drawBgBox(o["point"].x * this.boxSize, o["point"].y * this.boxSize);
    }.bind(this));

    this.clickedArr = [];
};

run.prototype.cleanAll = function () {
    for (let i = 0; i < this.bgHeightLength; i++) {
        for (let j = 0; j < this.bgWidthLength; j++) {
            this.cvs.beginPath();
            this.cvs.fillStyle = "#FFFFFF";
            this.cvs.fillRect(j * this.boxSize + 1, i * this.boxSize + 1, this.boxSize - 1, this.boxSize - 1);
            this.cvs.fill();
            this.cvs.stroke();
            this.cvs.closePath();
        }
    }
    this.clickedArr = [];
};

run.prototype.reset = function () {
    for (let i = 0; i < this.bgHeightLength; i++) {
        for (let j = 0; j < this.bgWidthLength; j++) {
            this.cvs.beginPath();
            this.cvs.fillStyle = "#e8e8e8";
            this.cvs.fillRect(j * this.boxSize + 1, i * this.boxSize + 1, this.boxSize - 1, this.boxSize - 1);
            this.cvs.fill();
            this.cvs.stroke();
            this.cvs.closePath();
        }
    }
    this.clickedArr = [];
};

run.prototype.drawBg = function () {

    for (let i = 0; i < this.bgHeightLength; i++) {
        for (let j = 0; j < this.bgWidthLength; j++) {
            this.drawBgBox(j * this.boxSize, i * this.boxSize);
        }
    }
};

run.prototype.drawBgBox = function (x, y, z) {

    this.cvs.beginPath();
    this.cvs.fillStyle = z ? this.clickedColor : this.bgColor;
    this.cvs.fillRect(x + 1, y + 1, this.boxSize - 1, this.boxSize - 1);
    this.cvs.fill();
    this.cvs.stroke();
    this.cvs.closePath();
};


let canvas = document.querySelector("#canvas");
let suggest1 = document.querySelector("#suggest1");
let suggest2 = document.querySelector("#suggest2");
let cvs = canvas.getContext("2d");
let a = new run(canvas, {}, true);
let sugs = [];
sugs.push(new run(suggest1, {}, false));
sugs.push(new run(suggest2, {}, false));
// let sug1 = new run(suggest1, {}, false);
// let sug2 = ;

function reset_suggestion(sugs, changeSize, size) {
    for (let i = 0; i < sugs.length; i++) {
        if (changeSize) {
            sugs[i].cleanAll();
            sugs[i].start(size);
        } else {
            sugs[i].reset();
        }
    }
    // sug.cleanAll();
    // sug.reset();
}

$('#small').on('click', function () {
    a.clean();
    a.cleanAll();
    a.start(8);
    reset_suggestion(sugs, true, 8);
});

$('#medium').on('click', function () {
    a.clean();
    a.cleanAll();
    a.start(12);
    reset_suggestion(sugs, true, 12);
});

$('#large').on('click', function () {
    a.clean();
    a.cleanAll();
    a.start(16);
    reset_suggestion(sugs, true, 16);
});

$("#base").on('click', function () {
    a.currentBrush = 1;
    a.changeClickColor("#00ff00")
});

$("#resource").on('click', function () {
    a.currentBrush = 2;
    a.changeClickColor("#0000ff")
});

$("#obstacle").on('click', function () {
    a.currentBrush = 3;
    a.changeClickColor("#ff0000")
});

$("#clean").on('click', function () {
    a.clean()
});

$("#show").on('click', function () {
    $("#res").text(a.showRes());
});
