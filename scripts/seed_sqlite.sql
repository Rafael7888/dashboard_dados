-- Apagar tabela se já existir
DROP TABLE IF EXISTS sales;

-- Criar tabela de vendas
CREATE TABLE sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    customer TEXT NOT NULL,
    product TEXT NOT NULL,
    category TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    total REAL,
    region TEXT NOT NULL,
    channel TEXT NOT NULL
);

-- Inserir dados de exemplo
INSERT INTO sales (date, customer, product, category, quantity, unit_price, total, region, channel) VALUES
('2023-01-15', 'Cliente A', 'Teclado Pro', 'Periféricos', 3, 29.90, 89.70, 'Norte', 'Online'),
('2023-01-20', 'Cliente B', 'Rato Gamer', 'Periféricos', 2, 24.50, 49.00, 'Centro', 'Loja'),
('2023-02-02', 'Cliente C', 'Monitor 24"', 'Monitores', 1, 129.00, 129.00, 'Lisboa', 'Online'),
('2023-02-18', 'Cliente D', 'Portátil 15"', 'Portáteis', 1, 799.00, 799.00, 'Sul', 'Loja'),
('2023-03-03', 'Cliente E', 'Headset Stereo', 'Áudio', 2, 39.90, 79.80, 'Norte', 'Online'),
('2023-03-21', 'Cliente F', 'Hub USB-C', 'Acessórios', 4, 14.90, 59.60, 'Lisboa', 'Online'),
('2023-04-04', 'Cliente G', 'Monitor 27"', 'Monitores', 1, 199.00, 199.00, 'Centro', 'Loja'),
('2023-04-17', 'Cliente H', 'Portátil 14"', 'Portáteis', 1, 699.00, 699.00, 'Norte', 'Online'),
('2023-05-09', 'Cliente I', 'Coluna Bluetooth', 'Áudio', 2, 49.90, 99.80, 'Sul', 'Loja'),
('2023-05-22', 'Cliente J', 'Disco SSD 1TB', 'Armazenamento', 1, 89.90, 89.90, 'Lisboa', 'Online');
