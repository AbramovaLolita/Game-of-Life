
from PIL import Image, ImageDraw

INPUT_FILE = 'init01.csv'
TEST_INPUT = 'test_input.csv'
OUTPUT_FILE_CSV = 'generation.csv'
OUTPUT_FILE_PNG = 'generation.png'
GENERATIONS = 20
CELL_SIZE = 45
BORDER_WIDTH = 2
DEBUG = True


def live_neighbors(grid, row, col):
    '''
    @requires: grid which is a list of lists where
      each list contains either 0 or 1 meaning the cell
      is alive (1) or dead (0). The size of all inner lists
      must be the same.
      E.g.,
        [ [0, 1, 0],
          [0, 0, 0],
          [1, 1, 0],
        ]
      row and col are integers such that 0 <= row <= number of rows in grid
      and 0 <= col <= number of columns in grid

    @modifies: None
    @effects: None
    @raises: None
    @returns: the number of cells whose value is 1
    '''
    rows = len(grid)
    cols = len(grid[0])
    count = 0
    if row >= 1:
        min_r = row - 1
    else:
        min_r = 0
    max_r = row + 1 if row < rows - 1 else row
    min_c = col - 1 if col >= 1 else 0
    max_c = col + 1 if col < cols - 1 else col
    ##print(f'{row} {col}')
    for idx_y in range(min_r, max_r + 1):
        for idx_x in range(min_c, max_c + 1):
            # print(f'The value of grid[{idx_x}][{idx_y}] is {grid[idx_y][idx_x]}')
            if idx_y == row and idx_x == col:
                continue
            if grid[idx_y][idx_x] == 1:
                count += 1
    return count


def model(grid):
    """
    @requires: grid which is a list of lists where
      each list contains either 0 or 1 meaning the cell
      is alive (1) or dead (0). The size of all inner lists
      must be the same.
      E.g.,
      [ [0, 1, 0],
        [0, 0, 0],
        [1, 1, 0],
      ]
    @modifies: None
    @effects: None
    @raises: None
    @returns: a new grid which follows the format of the
      input grid but with cell values that correspond to the new
      generation. The new generation is determined by applying
      the following rules:
          1. Any live cell with fewer than two live neighbours dies, as if by underpopulation.
          2. Any live cell with two or three live neighbours lives on to the next generation.
          3. Any live cell with more than three live neighbours dies, as if by overpopulation.
          4. Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
    """
    rows, cols = len(grid), len(grid[0])
    new_grid = [[0 for _ in range(cols)] for _ in range(rows)]
    for row in range(rows):
        for col in range(cols):
            live_nb = live_neighbors(grid, row, col)
            # Rule 1
            if live_nb < 2 and grid[row][col] == 1:
                new_grid[row][col] = 0
            # Rule 2
            elif 2 <= live_nb <= 3 and grid[row][col] == 1:
                new_grid[row][col] = 1
            # Rule 3
            elif live_nb > 3 and grid[row][col] == 1:
                new_grid[row][col] = 0
            # Rule 4
            elif grid[row][col] == 0 and live_nb == 3:
                new_grid[row][col] = 1
            else:
                new_grid[row][col] = 0
    return new_grid



def read_input(filename):
    '''
   @requires: CSV-файл с описанием исходного состояния колонии в формате:
      0;1:0
      1;0;1
      0;1;1
    @modifies: None
    @effects: None
    @raises: ValueError, FileNotFoundError
    @returns: grid - список списков в формате:
    [[0, 1, 0],
      [1, 0, 1],
      [0, 1, 1],
      ]
    '''
    grid = []
    try:
        with open(filename, "r") as input_file:
            lines = input_file.readlines()
        for line in lines:
            line = line.strip()
            line = line.split(';')
            line = [int(elem) for elem in line]
            grid.append(line)
        return grid
    except ValueError:
        return 'incorrect_file'
    except FileNotFoundError:
        return None



def count_generations(curr_grid, filename):
    '''
     @requires: grid - список списков в формате:
    [[0, 1, 0],
      [1, 0, 1],
      [0, 1, 1],
      ];
      CSV-файл с описанием исходного состояния колонии в формате:
      0;1:0
      1;0;1
      0;1;1
      как описание предыдущего состояния переменной grid.
      @modifies: None
      @effects: None
      @raises: None
      @returns: grid_age - список списков в формате:
      [[0, 1, 0],
        [1, 0, 1],
        [0, 1, 1],
        ] как итог сравнения текущей переменной grid с CVS-файлом
      '''
    rows, cols = len(curr_grid), len(curr_grid[0])
    grid = read_input(filename)
    grid_age = [[0 if curr_grid[row][col] == 0 else grid[row][col] + curr_grid [row][col] for col in range(cols)] for row in range(rows)]
    return grid_age

def write_output(grid, filename):
    '''
    @requires: grid which is a list of lists where
      each list contains either 0 or 1 meaning the cell
      is alive (1) or dead (0). The size of all inner lists
      must be the same.
      E.g.,
        [ [0, 1, 0],
          [0, 0, 0],
          [1, 1, 0],
        ]
      row and col are integers such that 0 <= row <= number of rows in grid
      and 0 <= col <= number of columns in grid;
      filename
        @modifies: None
        @effects: None
        @raises: None
        @returns: None
    '''
    with open(filename, 'w') as output_file:
        for i in range(len(grid)):
            output_file.write(f'{';'.join(map(str, grid[i]))}\n')


def write_png(grid, grid_age, filename):
    '''
    @requires: grid which is a list of lists where
    each list contains either 0 or 1 meaning the cell
    is alive (1) or dead (0). The size of all inner lists
    must be the same.
     E.g.,
     [ [0, 1, 0],
     [0, 0, 0],
     [1, 1, 0],
     ]
    row and col are integers such that 0 <= row <= number of rows in grid
    and 0 <= col <= number of columns in grid;
    filename
    @modifies: None
    @effects: None
    @raises: None
    @returns: None
      '''
    rows, cols = len(grid), len(grid[0])
    im = Image.new(mode='RGB', size=(cols * CELL_SIZE + CELL_SIZE,
                                     rows * (CELL_SIZE + BORDER_WIDTH) + BORDER_WIDTH), color=(255,240,245))
    draw = ImageDraw.Draw(im)
    id_y = 0
    id_x = 0
    age_color = 25
    for row in range(rows):
        draw.line(xy=(0, id_y, CELL_SIZE + CELL_SIZE * cols, id_y), fill=(188,143,143), width=BORDER_WIDTH)
        draw.line(xy=(id_x, 0, id_x, (CELL_SIZE + BORDER_WIDTH) * cols), fill=(188,143,143), width=BORDER_WIDTH)
        x = 0
        for col in range(cols):
            x += CELL_SIZE
            if grid[row][col] == 1:
                if grid_age[row][col] > 1:
                    draw.rectangle([(x, id_y + BORDER_WIDTH),
                                    (x + CELL_SIZE + 1, id_y + CELL_SIZE + BORDER_WIDTH)],
                                   fill=(255 - grid_age[row][col] ** 6, grid_age[row][col] ** 6, grid_age[row][col] ** 6),
                                   outline=(255, 182, 193))
                else:
                    draw.rectangle([(x, id_y + BORDER_WIDTH),
                                       (x + CELL_SIZE + 1, id_y + CELL_SIZE + BORDER_WIDTH)],
                                      fill=(255,0,0),
                                      outline=(255, 182, 193))
        id_y += BORDER_WIDTH + CELL_SIZE
        id_x +=  CELL_SIZE
    draw.line(xy=(0, id_y, CELL_SIZE + CELL_SIZE * cols, id_y), fill=(188, 143, 143), width=BORDER_WIDTH)
    draw.line(xy=(id_x, 0, id_x, (CELL_SIZE + BORDER_WIDTH) * cols), fill=(188, 143, 143), width=BORDER_WIDTH)
    im.save(filename)



if result := read_input(INPUT_FILE) is None:
    print('Файл не обнаружен или назван некорректно')
elif read_input(INPUT_FILE) == 'incorrect_file':
    print('Файл заполнен некорректно')
else:
    grid = read_input(INPUT_FILE)
    grid_age = count_generations(grid, INPUT_FILE)
    write_png(grid, grid_age, OUTPUT_FILE_PNG)
    png_list = []
    filename_csv = INPUT_FILE
    for gen in range(GENERATIONS):
        cur_model = model(grid)
        grid_age = count_generations(cur_model, filename_csv)
        filename_png = f'generation {gen}.png'
        filename_csv = f'generation {gen}.csv'
        write_output(cur_model, filename_csv)
        write_png(cur_model, grid_age, filename_png)
        curr_png = Image.open(filename_png)
        png_list.append(curr_png)
        grid = cur_model
    # создаем gif-визуализацию жизни колонии
    png_list[0].save(
        'generation.gif',
        save_all=True,
        append_images=png_list[1:],
        optimize=True,
        duration=100,
        loop=0)



if DEBUG:
    grid = read_input(TEST_INPUT)
    expected = \
        [[0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0],
         [0, 0, 0, 1, 1, 1],
         [0, 0, 0, 1, 1, 1],
         [0, 0, 0, 1, 0, 1],
         [0, 0, 0, 1, 1, 0]]
    actual = model(grid)
    write_output(actual, OUTPUT_FILE_CSV)
    if actual != expected:
        print('Test model failed!')

    expected = 0
    actual = live_neighbors(grid, 1, 0)
    if actual != expected:
        print('Test 1 live_neighbors failed!')
    actual = live_neighbors(grid, 2, 0)
    if actual != expected:
        print('Test 2 live_neighbors failed!')

    expected = 1
    actual = live_neighbors(grid, 3, 2)
    if actual != expected:
        print('Test 3 live_neighbors failed!')

    expected = 3
    actual = live_neighbors(grid, 4, 3)
    if actual != expected:
        print('Test 4 live_neighbors failed!')

else:
    grid = read_input(INPUT_FILE)

